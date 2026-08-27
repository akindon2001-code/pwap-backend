from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from core.models import TimeStamped

class BenefitClaim(TimeStamped):
    TYPES = ["retirement", "withdrawal", "disability", "death"]
    STAGES = ["SUBMITTED", "VALIDATED", "ACCRUED_RIGHTS", "CONTRIB_REVIEW",
              "COMPLIANCE", "AUTHORISED", "PAID"]
    claim_type = models.CharField(max_length=20)
    stage = models.CharField(max_length=20, default="SUBMITTED")
    submitted_at = models.DateTimeField(default=timezone.now)
    sla_hours = models.IntegerField(default=48)
    escalated = models.BooleanField(default=False)

    def clean(self):
        if self.claim_type not in self.TYPES:
            raise ValidationError("Unknown claim type: %s" % self.claim_type)
        if self.stage not in self.STAGES:
            raise ValidationError("Unknown stage: %s" % self.stage)

    def save(self, *a, **k):
        self.full_clean()
        super().save(*a, **k)

    def advance(self):
        i = self.STAGES.index(self.stage)
        if i >= len(self.STAGES) - 1:
            raise ValueError("Claim is already at the final stage")
        self.stage = self.STAGES[i + 1]
        self.save()

    def check_sla(self, now=None):
        now = now or timezone.now()
        if self.stage != "PAID" and (now - self.submitted_at) > timedelta(hours=self.sla_hours):
            if not self.escalated:
                self.escalated = True
                self.save()
        return self.escalated
