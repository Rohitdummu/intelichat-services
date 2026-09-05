from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_registration_and_login():
    email = "newuser@example.com"
    password = "StrongPass123!"

    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 200
    data = register.json()
    assert data["email"] == email
    assert "password_hash" not in data

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    payload = login.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"


def test_invalid_document_type_is_rejected():
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "docuser@example.com", "password": "StrongPass123!"},
    )
    token = register.json()["email"]
    assert token is not None
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "docuser@example.com", "password": "StrongPass123!"},
    )
    token_value = login.json()["access_token"]

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
        headers={"Authorization": f"Bearer {token_value}"},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_database_connectivity_health():
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"
