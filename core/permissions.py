"""Role-based access control used across the PWAP services."""
from django.http import HttpResponse, HttpResponseForbidden

ROLE_PERMISSIONS = {
    "contributor":           {"view_own_claim", "submit_change_request", "submit_claim"},
    "contributions_officer": {"review_change_request", "review_claim", "validate_remittance"},
    "operations_officer":    {"validate_remittance", "view_records"},
    "compliance_officer":    {"clear_claim", "view_audit"},
    "administrator":         {"*"},
}

def has_permission(role, permission):
    perms = ROLE_PERMISSIONS.get(role, set())
    return "*" in perms or permission in perms

def require_permission(permission):
    def decorator(view):
        def wrapped(request, *args, **kwargs):
            role = getattr(request, "role", None) or request.META.get("HTTP_X_ROLE")
            if not has_permission(role, permission):
                return HttpResponseForbidden("Forbidden")
            return view(request, *args, **kwargs)
        return wrapped
    return decorator

@require_permission("view_records")
def records_view(request):
    return HttpResponse("ok")
