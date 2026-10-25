"""
Demonstration Workflow Script for AI Medical Report Explainer.
Executes the full 10-step end-to-end user journey using synthetic medical data.
"""
import sys
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def run_demo():
    print("=" * 80)
    print("AI-POWERED MEDICAL REPORT ANALYSIS & PRESCRIPTION SYSTEM")
    print("END-TO-END DEMONSTRATION WORKFLOW (SYNTHETIC DATA ONLY)")
    print("=" * 80)

    # Step 1: User Registration and Login
    print("\n[Step 1] User Registration & Login")
    email = "college_demo_user@example.com"
    password = "StrongDemoPassword123!"

    reg_resp = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    if reg_resp.status_code == 201:
        print(f"-> Registered user: {email}")
    else:
        print(f"-> User already registered, proceeding to login.")

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token_data = login_resp.json()["data"]
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"-> Authentication successful. JWT token obtained (expires in {token_data['expires_in']}s).")

    # Step 2: Upload Sample Report
    print("\n[Step 2] User Uploads Sample CBC Report (PDF)")
    sample_pdf = backend_dir / "data" / "sample_reports" / "synthetic_cbc_report.pdf"
    assert sample_pdf.exists(), "Sample PDF not found. Run generate_sample_data.py first."

    with open(sample_pdf, "rb") as f:
        files = {"file": ("synthetic_cbc_report.pdf", f.read(), "application/pdf")}
        data = {"document_type": "report"}
        upload_resp = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)

    assert upload_resp.status_code == 201, f"Upload failed: {upload_resp.text}"
    doc_data = upload_resp.json()["data"]
    doc_id = doc_data["id"]
    print(f"-> Document uploaded successfully. ID: {doc_id}, Status: {doc_data['processing_status']}")

    # Step 3 & 4: Review Extracted OCR Text
    print("\n[Step 3 & 4] User Reviews Extracted OCR Text")
    text_resp = client.get(f"/api/v1/documents/{doc_id}/text", headers=headers)
    assert text_resp.status_code == 200
    extracted_text_data = text_resp.json()["data"]
    print(f"-> Extraction Status: {extracted_text_data['extraction_status']}")
    print(f"-> Word Count: {extracted_text_data['metadata'].get('total_word_count')}")
    preview = "\n".join(extracted_text_data["extracted_text"].splitlines()[:10])
    print(f"-> Text Preview:\n{preview}\n...")

    # Step 5: Backend Parses Lab Values & Generates Grounded AI Explanation
    print("\n[Step 5 & 6] Parse Laboratory Values & Request Plain-Language Explanation")
    analyze_resp = client.post(f"/api/v1/documents/{doc_id}/analyze", json={"include_rag_sources": True}, headers=headers)
    assert analyze_resp.status_code == 200, f"Analysis failed: {analyze_resp.text}"
    analysis = analyze_resp.json()["data"]
    print(f"-> Analysis ID: {analysis['id']}")
    print(f"-> Model Provider: {analysis['model_provider']}")
    print(f"-> Detected Stats: {analysis['stats']}")

    # Step 7 & 8: Verify Lab Values & RAG Sources
    print("\n[Step 7 & 8] Structured Values & Grounded Reference Sources")
    print("-" * 60)
    for val in analysis["laboratory_values"]:
        ref = val["reference_range"]["text_range"] if val["reference_range"] else "None provided"
        print(f"  * {val['test_name']:<18}: {val['value_text']} {val['unit']} | Range: {ref:<14} | Flag: {val['abnormality_status'].upper()}")

    print("\n-> Plain-Language Patient Summary:")
    print(f"   \"{analysis['summary']}\"")

    print("\n-> Key Educational Findings:")
    for finding in analysis["explanation"]["key_findings"]:
        print(f"   - {finding}")

    print("\n-> Suggested Questions For Healthcare Professional:")
    for q in analysis["explanation"]["questions_for_doctor"]:
        print(f"   ? {q}")

    # Step 9: Source Citations (Grounded RAG)
    print("\n[Step 9] Verified Reference Sources (Strictly Cited):")
    for src in analysis["sources"]:
        print(f"   [Source] {src['title']} ({src['publisher']})")
        if src.get("source_url"):
            print(f"            URL: {src['source_url']}")

    # Step 10: Prescription Workflow with Flagged Uncertainties
    print("\n[Step 10] Prescription Extraction with Safety & Human Confirmation Workflow")
    presc_pdf = backend_dir / "data" / "sample_reports" / "synthetic_prescription.pdf"
    with open(presc_pdf, "rb") as f:
        p_files = {"file": ("synthetic_prescription.pdf", f.read(), "application/pdf")}
        p_data = {"document_type": "prescription"}
        p_upload = client.post("/api/v1/documents/upload", files=p_files, data=p_data, headers=headers)

    p_doc_id = p_upload.json()["data"]["id"]
    p_proc = client.post(f"/api/v1/documents/{p_doc_id}/process-prescription", headers=headers)
    assert p_proc.status_code == 200
    p_list = p_proc.json()["data"]

    print(f"-> Total Prescriptions Detected: {p_list['total_items']}")
    print(f"-> Requires Human Review: {p_list['requires_human_review']}")

    uncertain_id = None
    for item in p_list["items"]:
        conf = item["confidence_metadata"].get("confidence_score", 1.0)
        needs_review = item["confidence_metadata"].get("needs_human_confirmation", False)
        print(f"  * Medicine: {item['extracted_medicine_name']:<15} | Strength: {str(item['extracted_strength']):<8} | Confidence: {conf} | Human Review Flag: {needs_review}")
        if needs_review and not uncertain_id:
            uncertain_id = item["id"]

    if uncertain_id:
        print(f"\n-> Simulating User Confirmation on uncertain medication item ({uncertain_id})...")
        confirm_resp = client.patch(
            f"/api/v1/prescriptions/{uncertain_id}/confirm",
            json={
                "confirmed_medicine_name": "ClarifiedMedication",
                "confirmed_strength": "10 mg",
                "status": "confirmed_by_user",
                "user_note": "Doctor confirmed medication name on phone.",
            },
            headers=headers,
        )
        assert confirm_resp.status_code == 200
        print(f"-> Item successfully verified by human user. Status: {confirm_resp.json()['data']['verification_status']}")

    print("\n" + "=" * 80)
    print("ALL 10 DEMONSTRATION WORKFLOW STAGES EXECUTED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
