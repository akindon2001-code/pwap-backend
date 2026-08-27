from django.core.exceptions import ValidationError
from django.db import models
from core.models import TimeStamped

class Contributor(TimeStamped):
    rsa_pin = models.CharField(max_length=15, unique=True)
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    bank_account = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, default="active")

    def clean(self):
        missing = [f for f in ("rsa_pin", "surname", "first_name") if not getattr(self, f)]
        if missing:
            raise ValidationError("Missing mandatory fields: %s" % ", ".join(missing))
        if not (self.rsa_pin.startswith("PEN") and len(self.rsa_pin) == 15):
            raise ValidationError("RSA PIN must be 15 characters and start with PEN")

    def save(self, *a, **k):
        self.full_clean()
        super().save(*a, **k)

class ChangeRequest(TimeStamped):
    PENDING, APPROVED, REJECTED = "PENDING", "APPROVED", "REJECTED"
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE)
    field = models.CharField(max_length=50)
    new_value = models.CharField(max_length=200)
    state = models.CharField(max_length=10, default=PENDING)

    def approve(self):
        if self.state != self.PENDING:
            raise ValueError("Only PENDING requests can be approved")
        setattr(self.contributor, self.field, self.new_value)
        self.contributor.save()
        self.state = self.APPROVED
        self.save()

    def reject(self):
        if self.state != self.PENDING:
            raise ValueError("Only PENDING requests can be rejected")
        self.state = self.REJECTED
        self.save()
