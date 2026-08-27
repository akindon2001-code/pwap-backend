from django.db.models.signals import post_save
from django.dispatch import receiver
from claims.models import BenefitClaim
from .models import AuditEvent

@receiver(post_save, sender=BenefitClaim)
def log_claim_event(sender, instance, created, **kwargs):
    AuditEvent.objects.create(
        event_type="CLAIM_CREATED" if created else "CLAIM_UPDATED",
        actor="system",
        source_ip="127.0.0.1",
        target_type="BenefitClaim",
        target_id=str(instance.id),
        action="stage=%s" % instance.stage,
        before={},
        after={"stage": instance.stage},
    )
