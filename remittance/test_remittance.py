import pytest
from contributors.models import Contributor
from remittance.services.validator import RemittanceValidator, ScheduleRecord

pytestmark = pytest.mark.django_db

def seed(pin="PEN100000000001", surname="Adebayo"):
    return Contributor.objects.create(rsa_pin=pin, surname=surname, first_name="Tunde")

def test_valid_record_passes():
    seed()
    v = RemittanceValidator()
    res = v.validate(ScheduleRecord(rsa_pin="PEN100000000001", surname="Adebayo", period="2025-07"))
    assert res.is_valid

def test_unknown_pin_is_blocking():
    v = RemittanceValidator()
    res = v.validate(ScheduleRecord(rsa_pin="PENZZZZZZZZZZZZ", surname="X", period="2025-07"))
    assert not res.is_valid
    assert len(res.exceptions) == 1
    assert res.exceptions[0].code == "RSA_PIN_NOT_FOUND"
    assert res.exceptions[0].blocking

def test_biodata_mismatch_flagged():
    seed(surname="Adebayo")
    v = RemittanceValidator()
    res = v.validate(ScheduleRecord(rsa_pin="PEN100000000001", surname="Okoro", period="2025-07"))
    codes = [e.code for e in res.exceptions]
    assert "BIODATA_MISMATCH" in codes

def test_continuity_gap_when_period_missing():
    seed()
    v = RemittanceValidator()
    res = v.validate(ScheduleRecord(rsa_pin="PEN100000000001", surname="Adebayo", period=""))
    codes = [e.code for e in res.exceptions]
    assert "CONTINUITY_GAP" in codes

def test_duplicate_detected_second_time():
    seed()
    v = RemittanceValidator()
    r1 = ScheduleRecord(rsa_pin="PEN100000000001", surname="Adebayo", period="2025-07")
    r2 = ScheduleRecord(rsa_pin="PEN100000000001", surname="Adebayo", period="2025-07")
    assert v.validate(r1).is_valid
    res2 = v.validate(r2)
    assert "DUPLICATE" in [e.code for e in res2.exceptions]

def test_blocking_stops_further_checks():
    v = RemittanceValidator()
    res = v.validate(ScheduleRecord(rsa_pin="PENZZZZZZZZZZZZ", surname="", period=""))
    # only the blocking PIN failure, not biodata/continuity/duplicate
    assert [e.code for e in res.exceptions] == ["RSA_PIN_NOT_FOUND"]

def test_batch_mixed_valid_and_invalid():
    seed()
    v = RemittanceValidator()
    records = [
        ScheduleRecord(rsa_pin="PEN100000000001", surname="Adebayo", period="2025-07"),
        ScheduleRecord(rsa_pin="PENBAD", surname="Y", period="2025-07"),
    ]
    results = [v.validate(r) for r in records]
    assert results[0].is_valid and not results[1].is_valid
