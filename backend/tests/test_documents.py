from pathlib import Path
from fastapi.testclient import TestClient


def test_upload_valid_pdf_and_extraction(client: TestClient, auth_headers_user_one: dict, sample_reports_dir: Path):
    pdf_path = sample_reports_dir / "synthetic_cbc_report.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_cbc_report.pdf", f.read(), "application/pdf")},
            data={"document_type": "report"},
            headers=auth_headers_user_one,
        )

    assert response.status_code == 201
    doc = response.json()["data"]
    doc_id = doc["id"]
    assert doc["original_filename"] == "synthetic_cbc_report.pdf"
    assert doc["processing_status"] in ("extracted", "completed")

    # Verify extracted text endpoint
    text_resp = client.get(f"/api/v1/documents/{doc_id}/text", headers=auth_headers_user_one)
    assert text_resp.status_code == 200
    text_data = text_resp.json()["data"]
    assert "Hemoglobin" in text_data["extracted_text"]
    assert "WBC Count" in text_data["extracted_text"]


def test_upload_valid_image(client: TestClient, auth_headers_user_one: dict, sample_reports_dir: Path):
    img_path = sample_reports_dir / "synthetic_cbc_image.png"
    assert img_path.exists()

    with open(img_path, "rb") as f:
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_cbc_image.png", f.read(), "image/png")},
            data={"document_type": "report"},
            headers=auth_headers_user_one,
        )

    assert response.status_code == 201
    doc = response.json()["data"]
    assert doc["mime_type"] == "image/png"


def test_upload_empty_file_rejected(client: TestClient, auth_headers_user_one: dict):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
        data={"document_type": "report"},
        headers=auth_headers_user_one,
    )
    assert response.status_code == 400
    res_json = response.json()
    err_text = res_json.get("detail") or res_json.get("message", "")
    assert "empty" in err_text.lower()


def test_upload_unsupported_format_rejected(client: TestClient, auth_headers_user_one: dict):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("script.exe", b"MZDummyExecutableBytes", "application/x-msdownload")},
        data={"document_type": "report"},
        headers=auth_headers_user_one,
    )
    assert response.status_code == 415


def test_upload_corrupted_file_rejected(client: TestClient, auth_headers_user_one: dict):
    # Has .pdf extension but corrupted content that does not have PDF header
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("corrupted.pdf", b"RandomCorruptBytesWithoutPdfHeader", "application/pdf")},
        data={"document_type": "report"},
        headers=auth_headers_user_one,
    )
    assert response.status_code == 415


def test_user_correct_extracted_text(client: TestClient, auth_headers_user_one: dict, sample_reports_dir: Path):
    pdf_path = sample_reports_dir / "synthetic_cbc_report.pdf"
    with open(pdf_path, "rb") as f:
        up_resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_cbc_report.pdf", f.read(), "application/pdf")},
            headers=auth_headers_user_one,
        )
    doc_id = up_resp.json()["data"]["id"]

    # User modifies extracted text to fix a typo
    corrected_text = "Hemoglobin 14.0 g/dL 12.0 - 16.0 NORMAL\nPlatelets 250 10^3/uL 150 - 450 NORMAL"
    patch_resp = client.patch(
        f"/api/v1/documents/{doc_id}/text",
        json={"extracted_text": corrected_text},
        headers=auth_headers_user_one,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["extraction_status"] == "user_corrected"
    assert "14.0" in patch_resp.json()["data"]["extracted_text"]


def test_document_deletion(client: TestClient, auth_headers_user_one: dict, sample_reports_dir: Path):
    pdf_path = sample_reports_dir / "synthetic_cbc_report.pdf"
    with open(pdf_path, "rb") as f:
        up_resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_cbc_report.pdf", f.read(), "application/pdf")},
            headers=auth_headers_user_one,
        )
    doc_id = up_resp.json()["data"]["id"]

    # Delete
    del_resp = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers_user_one)
    assert del_resp.status_code == 200

    # Ensure document no longer exists
    get_resp = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers_user_one)
    assert get_resp.status_code == 404
