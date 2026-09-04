"""
Security and input validation tests for decentralized-clinical-consent-agent.
Tests for HMAC audit integrity, PHI guard, metric validation, and security defaults.
"""
import sys
import os
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import AuditTrail, PHIGuard, SecurityException, assert_no_phi
from agents.models import SystemTaskPayload
from consent_ledger.models import FrontierPayload


# =============================================================================
# METRIC VALIDATION TESTS
# =============================================================================

class TestMetricValidation:
    """Test that NaN and Inf values are rejected in task payloads."""

    def test_nan_primary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("nan"))

    def test_inf_primary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("inf"))

    def test_neg_inf_secondary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=10.0,
                              secondary_metric=float("-inf"))

    def test_valid_finite_metrics_accepted(self):
        p = SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=10.0, secondary_metric=5.0)
        assert p.primary_metric == 10.0
        assert p.secondary_metric == 5.0

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError, match="empty"):
            SystemTaskPayload(task_id="", target_identifier="K1", primary_metric=10.0)

    def test_whitespace_only_task_id_rejected(self):
        with pytest.raises(ValueError, match="empty"):
            SystemTaskPayload(task_id="   ", target_identifier="K1", primary_metric=10.0)


# =============================================================================
# FRONTIER PAYLOAD VALIDATION TESTS
# =============================================================================

class TestFrontierPayloadValidation:
    """Test FrontierPayload dataclass validation."""

    def test_nan_primary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            FrontierPayload(task_id="T1", target_identifier="K1", primary_metric=float("nan"),
                            secondary_metric=5.0, status_descriptor="NOMINAL")

    def test_inf_secondary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            FrontierPayload(task_id="T1", target_identifier="K1", primary_metric=10.0,
                            secondary_metric=float("inf"), status_descriptor="NOMINAL")

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError, match="empty"):
            FrontierPayload(task_id="", target_identifier="K1", primary_metric=10.0,
                            secondary_metric=5.0, status_descriptor="NOMINAL")

    def test_valid_payload_accepted(self):
        p = FrontierPayload(task_id="T1", target_identifier="K1", primary_metric=10.0,
                            secondary_metric=5.0, status_descriptor="NOMINAL")
        assert p.primary_metric == 10.0


# =============================================================================
# HMAC AUDIT TRAIL TESTS
# =============================================================================

class TestAuditTrailIntegrity:
    """Test HMAC-SHA256 audit trail cryptographic integrity."""

    def test_audit_trail_chain_integrity(self):
        trail = AuditTrail(secret_key="test-key-for-integrity-verification")
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_B", {"data": "value2"})
        trail.log("actor3", "tier1", "EVENT_C", {"data": "value3"})
        assert trail.verify_integrity() is True

    def test_audit_trail_detects_tampering(self):
        trail = AuditTrail(secret_key="test-key-tamper-detection")
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_B", {"data": "value2"})
        # Tamper with an entry
        trail.logs[0]["payload_hash"] = "tampered_hash_value"
        assert trail.verify_integrity() is False

    def test_audit_trail_detects_signature_tampering(self):
        trail = AuditTrail(secret_key="test-key-sig-tamper")
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_B", {"data": "value2"})
        # Tamper with a signature
        trail.logs[1]["current_hash"] = "forged_signature"
        assert trail.verify_integrity() is False

    def test_audit_trail_empty_is_valid(self):
        trail = AuditTrail(secret_key="test-key-empty")
        assert trail.verify_integrity() is True

    def test_audit_trail_single_entry(self):
        trail = AuditTrail(secret_key="test-key-single")
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        assert trail.verify_integrity() is True

    def test_audit_trail_uses_env_var(self):
        os.environ["AUDIT_SECRET_KEY"] = "env-based-secret-key"
        trail = AuditTrail()
        assert trail.secret_key == b"env-based-secret-key"
        del os.environ["AUDIT_SECRET_KEY"]

    def test_audit_trail_rejects_phi_in_details(self):
        trail = AuditTrail(secret_key="test-key-phi")
        with pytest.raises(SecurityException):
            trail.log("actor1", "tier1", "EVENT_A", {"note": "Patient MRN-12345678"})


# =============================================================================
# PHI GUARD TESTS
# =============================================================================

class TestPHIGuard:
    """Test PHI outbound guard pattern matching."""

    def test_mrn_pattern_detected(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Patient MRN-12345678")

    def test_ssn_pattern_detected(self):
        with pytest.raises(SecurityException):
            assert_no_phi("SSN: 123-45-6789")

    def test_phone_pattern_detected(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Call 555-123-4567")

    def test_email_pattern_detected(self):
        with pytest.raises(SecurityException):
            assert_no_phi("Email: patient@example.com")

    def test_clean_text_passes(self):
        assert_no_phi("Analytical assay specimen KEY-001 optimal result")

    def test_empty_text_passes(self):
        assert_no_phi("")

    def test_phi_redaction(self):
        redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567")
        assert "555-123-4567" not in redacted
        assert "[REDACTED_IDENTIFIER]" in redacted
