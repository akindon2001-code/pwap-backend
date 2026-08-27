"""Remittance validation pipeline (Chapter 4, Appendix B)."""
from dataclasses import dataclass, field
from contributors.models import Contributor

@dataclass
class ScheduleRecord:
    rsa_pin: str
    surname: str = ""
    first_name: str = ""
    period: str = ""
    amount: float = 0.0
    employer_code: str = ""
    _contributor: object = None

@dataclass
class CheckOutcome:
    passed: bool
    code: str = ""
    blocking: bool = False
    @property
    def failed(self):
        return not self.passed
    @classmethod
    def ok(cls):
        return cls(True)
    @classmethod
    def fail(cls, code, blocking=False):
        return cls(False, code, blocking)

@dataclass
class ValidationResult:
    record: object
    exceptions: list = field(default_factory=list)
    @property
    def is_valid(self):
        return not self.exceptions
    def add(self, outcome):
        self.exceptions.append(outcome)

class RemittanceValidator:
    CHECKS = ["validate_pin", "validate_biodata", "validate_continuity", "detect_duplicate"]

    def __init__(self, seen_keys=None):
        self.seen = set(seen_keys or [])

    def validate(self, record):
        result = ValidationResult(record=record)
        for name in self.CHECKS:
            outcome = getattr(self, name)(record)
            if outcome.failed:
                result.add(outcome)
                if outcome.blocking:
                    break
        return result

    def validate_pin(self, r):
        c = Contributor.objects.filter(rsa_pin=r.rsa_pin).first()
        if not c:
            return CheckOutcome.fail("RSA_PIN_NOT_FOUND", blocking=True)
        r._contributor = c
        return CheckOutcome.ok()

    def validate_biodata(self, r):
        c = r._contributor
        if c and r.surname and c.surname.strip().lower() != r.surname.strip().lower():
            return CheckOutcome.fail("BIODATA_MISMATCH")
        return CheckOutcome.ok()

    def validate_continuity(self, r):
        if not r.period:
            return CheckOutcome.fail("CONTINUITY_GAP")
        return CheckOutcome.ok()

    def detect_duplicate(self, r):
        key = (r.rsa_pin, r.period)
        if key in self.seen:
            return CheckOutcome.fail("DUPLICATE")
        self.seen.add(key)
        return CheckOutcome.ok()
