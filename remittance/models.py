from django.db import models
from core.models import TimeStamped

class Employer(TimeStamped):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)

class RemittanceException(TimeStamped):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    rsa_pin = models.CharField(max_length=20)
    code = models.CharField(max_length=40)
    description = models.CharField(max_length=200, blank=True)
