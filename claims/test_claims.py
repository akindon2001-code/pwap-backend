import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from claims.models import BenefitClaim

pytestmark = pytest.mark.django_db

def test_all_claim_types_accepted():
    for t in BenefitClaim.TYPES:
        c = BenefitClaim.objects.create(claim_type=t)
        assert c.pk is not None

def test_unknown_type_rejected():
    with pytest.raises(ValidationError):
        BenefitClaim.objects.create(claim_type="lottery")

def test_advance_moves_one_stage():
    c = BenefitClaim.objects.create(claim_type="retirement")
    assert c.stage == "SUBMITTED"
    c.advance()
    assert c.stage == "VALIDATED"

def test_advance_full_lifecycle():
    c = BenefitClaim.objects.create(claim_type="retirement")
    for _ in range(len(BenefitClaim.STAGES) - 1):
        c.advance()
    assert c.stage == "PAID"

def test_cannot_advance_past_final():
    c = BenefitClaim.objects.create(claim_type="retirement")
    for _ in range(len(BenefitClaim.STAGES) - 1):
        c.advance()
    with pytest.raises(ValueError):
        c.advance()

def test_escalation_when_overdue():
    c = BenefitClaim.objects.create(claim_type="retirement", sla_hours=48)
    c.submitted_at = timezone.now() - timedelta(hours=72)
    c.save()
    assert c.check_sla() is True

def test_no_escalation_when_within_sla():
    c = BenefitClaim.objects.create(claim_type="retirement", sla_hours=48)
    assert c.check_sla() is False
