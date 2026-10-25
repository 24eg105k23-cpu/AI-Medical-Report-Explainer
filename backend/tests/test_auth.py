import pytest
from fastapi.testclient import TestClient
from app.models.user import User


def test_user_registration_success(client: TestClient):
    payload = {
        "email": "new_patient@example.com",
        "password": "StrongPassword123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "new_patient@example.com"
    assert "id" in data["data"]


def test_user_registration_duplicate_email(client: TestClient, user_one: User):
    payload = {
        "email": user_one.email,
        "password": "AnotherPassword123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_user_registration_weak_password(client: TestClient):
    payload = {
        "email": "weak_pw@example.com",
        "password": "short",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_user_login_success(client: TestClient, user_one: User):
    payload = {
        "email": user_one.email,
        "password": "PatientOneSecret123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


def test_user_login_invalid_password(client: TestClient, user_one: User):
    payload = {
        "email": user_one.email,
        "password": "WrongPassword!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


def test_get_current_user_profile(client: TestClient, auth_headers_user_one: dict, user_one: User):
    response = client.get("/api/v1/auth/me", headers=auth_headers_user_one)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email"] == user_one.email
    assert data["account_status"] == "active"


def test_unauthenticated_requests_rejected(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    response = client.get("/api/v1/documents")
    assert response.status_code == 401


def test_user_logout_and_revocation(client: TestClient, auth_headers_user_one: dict):
    # Perform logout
    logout_resp = client.post("/api/v1/auth/logout", headers=auth_headers_user_one)
    assert logout_resp.status_code == 200

    # Subsequent request using the same token should fail
    subsequent_resp = client.get("/api/v1/auth/me", headers=auth_headers_user_one)
    assert subsequent_resp.status_code == 401
