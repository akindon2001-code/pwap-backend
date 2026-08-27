#!/usr/bin/env python
"""
PWAP backend — scripted demonstration.

Runs a narrated, end-to-end walkthrough of the core domain logic:
  1. seed contributors
  2. validate a mixed employer remittance schedule (valid + faulty rows)
  3. submit a benefit claim and advance it through its lifecycle
  4. show the immutable, hash-chained audit trail

Run:  python demo.py
(Uses an in-memory database; nothing is persisted.)
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.runner import DiscoverRunner


def banner(title):
    print("\n" + "=" * 66)
    print("  " + title)
    print("=" * 66)


def run_demo():
    from contributors.models import Contributor, ChangeRequest
    from remittance.services.validator import RemittanceValidator, ScheduleRecord
    from claims.models import BenefitClaim
    from audit.models import AuditEvent

    banner("1. Seed contributor records (the RSA database)")
    people = [
        ("PEN100000000001", "Adebayo", "Tunde"),
        ("PEN100000000002", "Okonkwo", "Ngozi"),
        ("PEN100000000003", "Sani", "Musa"),
    ]
    for pin, surname, first in people:
        Contributor.objects.create(rsa_pin=pin, surname=surname, first_name=first)
        print(f"   + {pin}  {surname}, {first}")
    print(f"   {Contributor.objects.count()} contributors on file.")

    banner("2. Validate an employer remittance schedule (mixed quality)")
    schedule = [
        ScheduleRecord("PEN100000000001", "Adebayo", "Tunde", period="2025-07"),   # valid
        ScheduleRecord("PEN100000000002", "WRONGNAME", "Ngozi", period="2025-07"),  # biodata mismatch
        ScheduleRecord("PENZZZZZZZZZZZZ", "Ghost", "User", period="2025-07"),       # invalid PIN
        ScheduleRecord("PEN100000000003", "Sani", "Musa", period=""),               # continuity gap
        ScheduleRecord("PEN100000000001", "Adebayo", "Tunde", period="2025-07"),    # duplicate
    ]
    v = RemittanceValidator()
    posted, exceptions = 0, []
    for i, rec in enumerate(schedule, 1):
        result = v.validate(rec)
        if result.is_valid:
            posted += 1
            print(f"   row {i}: POSTED           ({rec.rsa_pin})")
        else:
            codes = ", ".join(e.code for e in result.exceptions)
            exceptions.append((i, codes))
            print(f"   row {i}: EXCEPTION -> {codes}")
    print(f"\n   {posted} posted, {len(exceptions)} exceptions returned for correction.")

    banner("3. Submit a benefit claim and advance it through the workflow")
    claim = BenefitClaim.objects.create(claim_type="retirement")
    print(f"   claim #{claim.id} created at stage: {claim.stage}")
    while claim.stage != "PAID":
        claim.advance()
        print(f"     -> {claim.stage}")
    print("   claim reached final stage (PAID).")

    banner("4. Immutable audit trail (SHA-256 tamper-evidence)")
    for ev in AuditEvent.objects.filter(target_type="BenefitClaim").order_by("id"):
        ok = "verified" if ev.verify() else "TAMPERED"
        print(f"   {ev.event_type:14s} {ev.action:14s} hash={ev.content_hash[:16]}... [{ok}]")
    print("\n   Demonstrating tamper detection:")
    ev = AuditEvent.objects.filter(target_type="BenefitClaim").first()
    ev.action = "stage=FORGED"
    ev.save()   # stored hash is not recomputed
    print(f"   after forging one record -> verify() = {ev.verify()}  (integrity breach detected)")

    banner("Demo complete")


if __name__ == "__main__":
    setup_test_environment()
    runner = DiscoverRunner(verbosity=0)
    old_config = runner.setup_databases()
    try:
        run_demo()
    finally:
        runner.teardown_databases(old_config)
        teardown_test_environment()
