"""Tests for the authentication endpoints (register, login, /me)."""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import os

# Force a test-only database to avoid polluting production data
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-tests-only!!"


def _get_client():
    """Create a TestClient with DB tables initialised."""
    from app.domain.models.user import User  # noqa: F401 — register table
    from app.infrastructure.db.sqlite_client import init_db
    init_db()
    from app.main import app
    return TestClient(app)


@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_register_and_login(mock_gdb, mock_seed):
    """Register a new user, then login with same credentials."""
    mock_gdb.driver.return_value = MagicMock()
    client = _get_client()

    # ── Register ──
    res = client.post("/api/v1/auth/register", json={
        "email": "test_booth_001@innovateindia.gov",
        "password": "securepass123",
        "role": "booth",
        "display_name": "Test Booth"
    })
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "booth"
    assert data["user"]["email"] == "test_booth_001@innovateindia.gov"
    token = data["access_token"]

    # ── Login ──
    res = client.post("/api/v1/auth/login", json={
        "email": "test_booth_001@innovateindia.gov",
        "password": "securepass123"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data

    # ── /me ──
    res = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert res.status_code == 200, res.text
    me = res.json()
    assert me["email"] == "test_booth_001@innovateindia.gov"
    assert me["role"] == "booth"


@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_login_invalid_credentials(mock_gdb, mock_seed):
    """Login with wrong password should return 401."""
    mock_gdb.driver.return_value = MagicMock()
    client = _get_client()

    res = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@innovateindia.gov",
        "password": "wrongpass"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "invalid-credentials"


@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_register_duplicate_email(mock_gdb, mock_seed):
    """Registering with an existing email should return 409."""
    mock_gdb.driver.return_value = MagicMock()
    client = _get_client()

    payload = {
        "email": "duplicate_test@innovateindia.gov",
        "password": "securepass123",
        "role": "official"
    }

    # First registration should succeed
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201

    # Second registration with same email should fail
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409
    assert res.json()["detail"] == "email-already-in-use"


@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_me_without_token(mock_gdb, mock_seed):
    """/me without token should return 401."""
    mock_gdb.driver.return_value = MagicMock()
    client = _get_client()

    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
