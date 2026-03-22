"""Tests for API endpoints using FastAPI TestClient."""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# ─── Health endpoint ────────────────────────────────────────────────────


@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_health_endpoint(mock_gdb, mock_seed):
    """GET / should return a health check response."""
    mock_driver = MagicMock()
    mock_gdb.driver.return_value = mock_driver
    from app.main import app

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Backend running"


# ─── Admin overview endpoint ────────────────────────────────────────────


@patch("app.api.v1.endpoints.admin.neo4j_client")
@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_admin_overview(mock_gdb, mock_seed, mock_client):
    """GET /api/v1/admin/overview should return booth/complaint stats."""
    mock_client.run_query.side_effect = [
        [
            {
                "total_booths": 5,
                "total_complaints": 20,
                "total_open": 8,
                "total_resolved": 12,
            }
        ],
    ]
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/v1/admin/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_booths"] == 5
    assert data["total_complaints"] == 20
    assert data["total_open_complaints"] == 8
    assert data["total_resolved_complaints"] == 12


# ─── Admin booths endpoint ─────────────────────────────────────────────


@patch("app.api.v1.endpoints.admin.neo4j_client")
@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_admin_booths(mock_gdb, mock_seed, mock_client):
    """GET /api/v1/admin/booths should return booth list."""
    mock_client.run_query.return_value = [
        {
            "booth_id": 1,
            "complaint_count": 10,
            "open_count": 3,
            "resolved_count": 7,
            "risk_level": "Medium",
            "recommendation": "Monitor situation",
        }
    ]
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/v1/admin/booths")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["booth_id"] == 1


# ─── Ask endpoint ──────────────────────────────────────────────────────


@patch("app.api.v1.endpoints.admin.neo4j_client")
@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_ask_rejects_empty_question(mock_gdb, mock_seed, mock_client):
    """POST /api/v1/ask should reject empty questions."""
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/v1/ask", json={"question": "   "})
    assert response.status_code == 400


@patch("app.api.v1.endpoints.admin.neo4j_client")
@patch("app.domain.services.seed_graph.seed")
@patch("app.infrastructure.db.neo4j_client.GraphDatabase")
def test_ask_requires_question_field(mock_gdb, mock_seed, mock_client):
    """POST /api/v1/ask should return 422 if 'question' is missing."""
    from app.main import app

    client = TestClient(app)
    response = client.post("/api/v1/ask", json={})
    assert response.status_code == 422
