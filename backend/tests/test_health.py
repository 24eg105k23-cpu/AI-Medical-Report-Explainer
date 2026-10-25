from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_connected"] is True
    assert data["ocr_engine_available"] is True
    assert data["llm_provider"] == "mock"


def test_readiness_probe(client: TestClient):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
