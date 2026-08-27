import pytest
from audit.models import AuditEvent
from claims.models import BenefitClaim

pytestmark = pytest.mark.django_db

def test_signal_creates_audit_event_on_claim_create():
    BenefitClaim.objects.create(claim_type="retirement")
    assert AuditEvent.objects.filter(target_type="BenefitClaim").count() >= 1

def test_all_nine_mandatory_fields_present():
    BenefitClaim.objects.create(claim_type="withdrawal")
    ev = AuditEvent.objects.latest("id")
    for f in AuditEvent.MANDATORY:
        assert getattr(ev, f) is not None

def test_hash_is_computed_on_save():
    ev = AuditEvent.objects.create(event_type="X", actor="a", target_type="T",
                                   target_id="1", action="did")
    assert len(ev.content_hash) == 64

def test_verify_true_for_untampered():
    ev = AuditEvent.objects.create(event_type="X", actor="a", target_type="T",
                                   target_id="1", action="did")
    assert ev.verify() is True

def test_verify_false_after_tamper():
    ev = AuditEvent.objects.create(event_type="X", actor="a", target_type="T",
                                   target_id="1", action="did")
    ev.action = "tampered"
    ev.save()  # content_hash already set, so not recomputed
    assert ev.verify() is False

def test_update_generates_second_event():
    c = BenefitClaim.objects.create(claim_type="retirement")
    before = AuditEvent.objects.count()
    c.advance()
    assert AuditEvent.objects.count() == before + 1
