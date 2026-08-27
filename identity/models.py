import hashlib
from django.db import models

class BiometricTemplate(models.Model):
    contributor_pin = models.CharField(max_length=20, unique=True)
    template_hash = models.CharField(max_length=64)

class SecurityEvent(models.Model):
    pin = models.CharField(max_length=20)
    kind = models.CharField(max_length=40)
    at = models.DateTimeField(auto_now_add=True)

def _transform(raw):
    """One-way transform of a raw biometric capture into a stored template."""
    return hashlib.sha256(("pwap-salt::" + raw).encode()).hexdigest()

def enrol(pin, raw):
    return BiometricTemplate.objects.create(contributor_pin=pin, template_hash=_transform(raw))

def verify(pin, raw):
    t = BiometricTemplate.objects.filter(contributor_pin=pin).first()
    if t and t.template_hash == _transform(raw):
        return True
    SecurityEvent.objects.create(pin=pin, kind="BIOMETRIC_NONMATCH")
    return False
