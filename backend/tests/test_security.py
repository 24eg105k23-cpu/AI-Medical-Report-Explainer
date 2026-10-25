from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.document_storage import document_storage


def test_cross_user_document_access_prevention(
    client: TestClient,
    auth_headers_user_one: dict,
    auth_headers_user_two: dict,
    sample_reports_dir: Path,
):
    """
    CRITICAL IDOR SECURITY TEST:
    User 2 MUST NOT be able to view, edit, or delete User 1's documents.
    """
    pdf_path = sample_reports_dir / "synthetic_cbc_report.pdf"
    with open(pdf_path, "rb") as f:
        up_resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_cbc_report.pdf", f.read(), "application/pdf")},
            headers=auth_headers_user_one,
        )
    user_one_doc_id = up_resp.json()["data"]["id"]

    # 1. User 2 tries to GET User 1's document -> 403 Forbidden
    cross_get = client.get(f"/api/v1/documents/{user_one_doc_id}", headers=auth_headers_user_two)
    assert cross_get.status_code == 403

    # 2. User 2 tries to GET User 1's OCR text -> 403 Forbidden
    cross_text = client.get(f"/api/v1/documents/{user_one_doc_id}/text", headers=auth_headers_user_two)
    assert cross_text.status_code == 403

    # 3. User 2 tries to PATCH User 1's OCR text -> 403 Forbidden
    cross_patch = client.patch(
        f"/api/v1/documents/{user_one_doc_id}/text",
        json={"extracted_text": "HackedText"},
        headers=auth_headers_user_two,
    )
    assert cross_patch.status_code == 403

    # 4. User 2 tries to DELETE User 1's document -> 403 Forbidden
    cross_delete = client.delete(f"/api/v1/documents/{user_one_doc_id}", headers=auth_headers_user_two)
    assert cross_delete.status_code == 403


def test_cross_user_analysis_access_prevention(
    client: TestClient,
    auth_headers_user_one: dict,
    auth_headers_user_two: dict,
    sample_reports_dir: Path,
):
    """
    User 2 MUST NOT be able to access User 1's generated analysis.
    """
    pdf_path = sample_reports_dir / "synthetic_cbc_report.pdf"
    with open(pdf_path, "rb") as f:
        up_resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("synthetic_cbc_report.pdf", f.read(), "application/pdf")},
            headers=auth_headers_user_one,
        )
    doc_id = up_resp.json()["data"]["id"]

    # User 1 analyzes the document
    an_resp = client.post(f"/api/v1/documents/{doc_id}/analyze", headers=auth_headers_user_one)
    analysis_id = an_resp.json()["data"]["id"]

    # User 2 tries to GET User 1's analysis -> 403 Forbidden
    cross_an_get = client.get(f"/api/v1/analyses/{analysis_id}", headers=auth_headers_user_two)
    assert cross_an_get.status_code == 403


def test_path_traversal_prevention():
    """
    Verify storage service rejects relative directory traversal keys like '../../etc/passwd'.
    """
    with pytest.raises(Exception):
        document_storage.get_file_path("../../windows/win.ini")


def test_database_model_unique_constraints(db_session: Session):
    """
    Verify database schema enforces uniqueness on User.email.
    """
    user_a = User(email="unique_email@example.com", password_hash="hash1", account_status="active")
    db_session.add(user_a)
    db_session.commit()

    user_b = User(email="unique_email@example.com", password_hash="hash2", account_status="active")
    db_session.add(user_b)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
