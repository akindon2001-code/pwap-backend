import pytest
from django.core.exceptions import ValidationError
from contributors.models import Contributor, ChangeRequest

pytestmark = pytest.mark.django_db

def make(pin="PEN100000000001", surname="Adebayo", first="Tunde"):
    return Contributor.objects.create(rsa_pin=pin, surname=surname, first_name=first)

def test_valid_contributor_saves():
    c = make()
    assert c.pk is not None and c.status == "active"

def test_missing_surname_rejected():
    with pytest.raises(ValidationError):
        Contributor.objects.create(rsa_pin="PEN100000000002", surname="", first_name="X")

def test_bad_pin_format_rejected():
    with pytest.raises(ValidationError):
        Contributor.objects.create(rsa_pin="123", surname="A", first_name="B")

def test_duplicate_pin_rejected():
    make()
    with pytest.raises(Exception):
        make()  # same pin

def test_change_request_approve_applies_value():
    c = make()
    cr = ChangeRequest.objects.create(contributor=c, field="bank_account", new_value="0123456789")
    cr.approve()
    c.refresh_from_db()
    assert cr.state == ChangeRequest.APPROVED and c.bank_account == "0123456789"

def test_change_request_reject():
    c = make()
    cr = ChangeRequest.objects.create(contributor=c, field="bank_account", new_value="0")
    cr.reject()
    assert cr.state == ChangeRequest.REJECTED

def test_cannot_approve_twice():
    c = make()
    cr = ChangeRequest.objects.create(contributor=c, field="bank_account", new_value="0123456789")
    cr.approve()
    with pytest.raises(ValueError):
        cr.approve()

def test_cannot_reject_approved():
    c = make()
    cr = ChangeRequest.objects.create(contributor=c, field="bank_account", new_value="0123456789")
    cr.approve()
    with pytest.raises(ValueError):
        cr.reject()
