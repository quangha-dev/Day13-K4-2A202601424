from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app


def test_correlation_id_generated_and_headers_present(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "user-123",
                "session_id": "sess-456",
                "feature": "search",
                "message": "Hello world",
            },
        )

    assert response.status_code == 200
    cid = response.headers.get("x-request-id")
    assert cid is not None
    assert re.match(r"^req-[0-9a-f]{8}$", cid)
    assert response.json()["correlation_id"] == cid
    assert "x-response-time-ms" in response.headers

    # Check logs enrichment
    lines = log_path.read_text(encoding="utf-8").splitlines()
    events = [json.loads(line) for line in lines if line.strip()]
    req_received = next(e for e in events if e.get("event") == "request_received")
    assert req_received["correlation_id"] == cid
    assert "user_id_hash" in req_received
    assert req_received["session_id"] == "sess-456"
    assert req_received["feature"] == "search"
    assert "model" in req_received
    assert "env" in req_received


def test_correlation_id_propagates_client_header(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    custom_id = "custom-client-req-999"
    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": custom_id},
            json={
                "user_id": "user-123",
                "session_id": "sess-456",
                "feature": "summary",
                "message": "Summarize this",
            },
        )

    assert response.status_code == 200
    assert response.headers.get("x-request-id") == custom_id
    assert response.json()["correlation_id"] == custom_id


def test_error_response_contains_correlation_id_header(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    # Enable incident to trigger error or post invalid endpoint
    custom_id = "error-test-cid-123"
    with TestClient(app) as client:
        client.post("/incidents/slow_responses/enable")
        # Post to invalid incident disable to raise 404
        response = client.post("/incidents/nonexistent_incident/disable", headers={"x-request-id": custom_id})

    assert response.headers.get("x-request-id") == custom_id
    assert response.status_code == 404
