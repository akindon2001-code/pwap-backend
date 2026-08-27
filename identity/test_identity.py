import pytest
from identity.models import enrol, verify, SecurityEvent

pytestmark = pytest.mark.django_db

def test_enrol_then_verify_matches():
    enrol("PEN100000000001", "fingerprint-raw-A")
    assert verify("PEN100000000001", "fingerprint-raw-A") is True

def test_nonmatch_returns_false_and_logs_security_event():
    enrol("PEN100000000001", "fingerprint-raw-A")
    assert verify("PEN100000000001", "fingerprint-raw-B") is False
    assert SecurityEvent.objects.filter(kind="BIOMETRIC_NONMATCH").count() == 1

def test_unknown_pin_returns_false():
    assert verify("PENDOESNOTEXIST", "x") is False

def test_stored_template_is_not_raw():
    t = enrol("PEN100000000002", "raw-secret")
    assert t.template_hash != "raw-secret" and len(t.template_hash) == 64
