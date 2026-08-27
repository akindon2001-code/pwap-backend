import hashlib
import json
from django.db import models
from django.utils import timezone

class AuditEvent(models.Model):
    MANDATORY = ["event_type", "actor", "source_ip", "target_type",
                 "target_id", "action", "before", "after", "timestamp"]
    event_type = models.CharField(max_length=50)
    actor = models.CharField(max_length=100)
    source_ip = models.CharField(max_length=45, blank=True)
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=50)
    action = models.CharField(max_length=200)
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now)
    content_hash = models.CharField(max_length=64, blank=True)

    def compute_hash(self):
        payload = json.dumps({
            "event_type": self.event_type, "actor": self.actor,
            "source_ip": self.source_ip, "target_type": self.target_type,
            "target_id": self.target_id, "action": self.action,
            "before": self.before, "after": self.after,
            "timestamp": self.timestamp.isoformat(),
        }, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()

    def save(self, *a, **k):
        if not self.content_hash:
            self.content_hash = self.compute_hash()
        super().save(*a, **k)

    def verify(self):
        """Tamper-evidence check: recompute and compare to stored hash."""
        return self.content_hash == self.compute_hash()
