from pathlib import Path
from fastapi.testclient import TestClient
from app.services.prescription_parser import prescription_parser


def test_prescription_parser_flags_uncertainty():
    text = (
        "1. Tab Amoxicillin 500mg 1 tab TID x 7 days PO\n"
        "2. AmbiguousDrug? 10?? Once daily\n"
    )
    items = prescription_parser.parse_prescription_text(text)
    assert len(items) == 2

    amox = next(i for i in items if "Amoxicillin" in i["extracted_medicine_name"])
    assert amox["extracted_strength"] == "500mg"
    assert amox["confidence_metadata"]["confidence_score"] >= 0.85

    ambig = next(i for i in items if "AmbiguousDrug" in i["extracted_medicine_name"])
    # Ambiguous drug with questions and missing strength MUST be flagged for human confirmation
    assert ambig["confidence_metadata"]["needs_human_confirmation"] is True
    assert ambig["confidence_metadata"]["confidence_score"] < 0.8


def test_prescription_processing_and_confirmation_api(
    client: TestClient,
    auth_headers_user_one: dict,
    sample_reports_dir: Path,
):
    pdf_path = sample_reports_dir / "synthetic_prescription.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        up_resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_prescription.pdf", f.read(), "application/pdf")},
            data={"document_type": "prescription"},
            headers=auth_headers_user_one,
        )
    assert up_resp.status_code == 201
    doc_id = up_resp.json()["data"]["id"]

    # Process prescription
    proc_resp = client.post(f"/api/v1/documents/{doc_id}/process-prescription", headers=auth_headers_user_one)
    assert proc_resp.status_code == 200
    p_data = proc_resp.json()["data"]
    assert p_data["total_items"] > 0
    assert p_data["requires_human_review"] is True

    # Find the flagged item
    flagged_item = next(
        it for it in p_data["items"]
        if it["confidence_metadata"].get("needs_human_confirmation") is True
    )

    # Human user verifies and confirms the item
    confirm_resp = client.patch(
        f"/api/v1/prescriptions/{flagged_item['id']}/confirm",
        json={
            "confirmed_medicine_name": "VerifiedAntibiotic",
            "confirmed_strength": "250mg",
            "status": "confirmed_by_user",
            "user_note": "Verified with pharmacy records",
        },
        headers=auth_headers_user_one,
    )
    assert confirm_resp.status_code == 200
    confirmed_data = confirm_resp.json()["data"]
    assert confirmed_data["extracted_medicine_name"] == "VerifiedAntibiotic"
    assert confirmed_data["verification_status"] == "confirmed_by_user"
