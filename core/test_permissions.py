import pytest
from django.test import RequestFactory
from core.permissions import has_permission, records_view

def test_admin_has_all():
    assert has_permission("administrator", "anything")

def test_role_specific_permission_granted():
    assert has_permission("operations_officer", "view_records")

def test_cross_role_denied():
    assert not has_permission("contributor", "view_records")

def test_unknown_role_denied():
    assert not has_permission(None, "view_records")

def test_view_returns_403_for_wrong_role():
    req = RequestFactory().get("/records/", HTTP_X_ROLE="contributor")
    assert records_view(req).status_code == 403

def test_view_allows_correct_role():
    req = RequestFactory().get("/records/", HTTP_X_ROLE="operations_officer")
    assert records_view(req).status_code == 200
