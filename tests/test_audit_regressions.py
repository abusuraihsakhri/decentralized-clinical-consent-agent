"""Regression tests for API access, CSV parsing, nested identifiers, and audit snapshots."""
import csv

import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main as primary_main
from consent_ledger.cli import main as legacy_main
from consent_ledger.server import create_app as create_legacy_app


def test_api_requires_configured_token(monkeypatch):
    monkeypatch.delenv("API_AUTH_TOKEN", raising=False)
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/metrics").status_code == 503
    assert client.post("/api/chat", json={"query": "status"}).status_code == 503
    monkeypatch.setenv("API_AUTH_TOKEN", "test-token-never-deploy")
    assert client.get("/api/audit/logs").status_code == 401
    assert client.get("/metrics", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/metrics", headers={"Authorization": "Bearer test-token-never-deploy"}).status_code == 200


def test_nested_identifiers_are_rejected(monkeypatch):
    monkeypatch.setenv("API_AUTH_TOKEN", "test-token-never-deploy")
    client = TestClient(app)
    payload = {
        "task_id": "T100",
        "target_identifier": "SYNTH-001",
        "primary_metric": 1.0,
        "attributes": {"nested": {"contact": "patient@example.com"}},
    }
    response = client.post("/api/audit", json=payload, headers={"Authorization": "Bearer test-token-never-deploy"})
    assert response.status_code == 422
    assert "patient@example.com" not in response.text
    supervisor = SystemSupervisor()
    with pytest.raises(SecurityException):
        supervisor.process_task(SystemTaskPayload(**payload))


def test_alternate_api_authentication(monkeypatch):
    monkeypatch.setenv("API_AUTH_TOKEN", "test-token-never-deploy")
    client = TestClient(create_legacy_app())
    assert client.get("/health").status_code == 200
    assert client.post("/api/chat", json={"query": "status"}).status_code == 401

    response = client.post(
        "/api/audit",
        json={
            "task_id": "DEMO-1", "target_identifier": "SYNTH-1",
            "primary_metric": 1.0, "secondary_metric": 1.0,
            "status_descriptor": "NOMINAL",
            "attributes": {"contact": "patient@example.com"},
        },
        headers={"Authorization": "Bearer test-token-never-deploy"},
    )
    assert response.status_code == 422
    assert "patient@example.com" not in response.text


def test_audit_trail_returns_isolated_copy():
    trail = AuditTrail(secret_key="regression-test")
    trail.log("system", "supervisor", "EVENT", {"status": "SUCCESS"})
    detached = trail.get_trail()
    detached[0]["current_hash"] = "tampered"
    assert trail.verify_integrity()
    assert trail.get_trail()[0]["current_hash"] != "tampered"


@pytest.mark.parametrize("entrypoint", [primary_main, legacy_main])
def test_batch_false_flag_is_not_critical(tmp_path, entrypoint):
    src = tmp_path / "input.csv"
    dest = tmp_path / "output.csv"
    src.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "DEMO-1,SYNTH-1,1,1,False,NOMINAL\n"
        "DEMO-2,SYNTH-2,1,1,True,NOMINAL\n",
        encoding="utf-8",
    )
    assert entrypoint(["batch", "-i", str(src), "-o", str(dest)]) == 0
    with dest.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    if entrypoint is primary_main:
        assert rows[0]["overall_urgency"] == "ROUTINE"
        assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"
    else:
        assert rows[0]["overall_status"] == "NOMINAL_OPTIMAL"
        assert rows[1]["overall_status"] == "CRITICAL_INTERVENTION_REQUIRED"


@pytest.mark.parametrize("entrypoint", [primary_main, legacy_main])
def test_batch_rejects_ambiguous_boolean(tmp_path, entrypoint):
    src = tmp_path / "input.csv"
    src.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "DEMO,SYNTH,1,1,maybe,NOMINAL\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Invalid is_critical_flag"):
        entrypoint(["batch", "-i", str(src), "-o", str(tmp_path / "out.csv")])
