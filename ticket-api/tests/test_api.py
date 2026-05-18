"""API tests — run against local ticket-api (docker compose up)."""

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    os.getenv("TEST_DATABASE_URL", "mysql+pymysql://ticket:ticket_secret@127.0.0.1:3307/filmarchive_wallet"),
)
os.environ.setdefault("TICKET_API_KEY", "dev-local-key")

from app.main import app  # noqa: E402

client = TestClient(app)
HEADERS = {"X-API-Key": "dev-local-key"}


@pytest.fixture
def electronic_extract():
    return {
        "movie_title": "花样年华",
        "show_date": "2026-03-15",
        "show_time": "19:30",
        "cinema_name": "中国电影资料馆",
        "hall_name": "1号厅",
        "payment_status": "已支付",
        "price": 45.0,
        "confidence": {},
        "missing_fields": [],
    }


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_draft_and_confirm_electronic(electronic_extract):
    r = client.post(
        "/api/drafts",
        json={"ticket_type": "electronic", "extract_json": electronic_extract},
        headers=HEADERS,
    )
    if r.status_code >= 500:
        pytest.skip(f"DB unavailable: {r.text}")
    assert r.status_code == 200
    draft_id = r.json()["draft_id"]

    r2 = client.post("/api/tickets/confirm", json={"draft_id": draft_id}, headers=HEADERS)
    assert r2.status_code == 200
    body = r2.json()
    assert body["ticket_id"] > 0
    assert "花样年华" in body["summary"]


def test_list_and_report(electronic_extract):
    r = client.get("/api/tickets", headers=HEADERS)
    if r.status_code >= 500:
        pytest.skip("DB unavailable")
    assert r.status_code == 200
    assert "items" in r.json()

    r2 = client.get("/api/reports/summary", headers=HEADERS)
    assert r2.status_code == 200
    assert "total_tickets" in r2.json()
