# PWAP Backend — Reference Implementation

[![CI](https://github.com/akindon2001-code/pwap-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/akindon2001-code/pwap-backend/actions/workflows/ci.yml)

A runnable Django implementation of the core backend logic of the **Pension
Workflow Automation Platform (PWAP)**, with an automated test suite and coverage
reporting.

> **Scope.** This is a **reference / prototype implementation of the domain
> logic** described in Chapter 4 of the dissertation — not the full production
> system. It has no Oracle, Camunda engine, biometric hardware or live
> PenCom/COBRA/Remita integration; it uses an in-memory SQLite database. Every
> figure it reports (tests, coverage) is produced by actually running the code.

## Modules
| Package | Responsibility |
|---|---|
| `contributors/` | Contributor records with field validation; change-request approval state machine |
| `remittance/` | Remittance validation pipeline: PIN, biodata, continuity, duplicate checks |
| `claims/` | Benefit-claim seven-stage lifecycle with SLA escalation |
| `audit/` | Immutable audit events with SHA-256 tamper-evidence (via Django signals) |
| `identity/` | One-way biometric template storage and verification |
| `integration/` | Retry-with-backoff and circuit-breaker resilience patterns |
| `core/` | Shared base model and role-based access control (RBAC) |

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest --cov --cov-report=term-missing               # run the suite: 43 passed, 99% coverage
coverage html                                        # browsable report at htmlcov/index.html
python demo.py                                        # narrated end-to-end walkthrough
```

## Test results (reproducible)
| Module | Tests | Passing | Coverage |
|---|:-:|:-:|:-:|
| Contributor Management | 8 | 8 | 100% |
| Remittance Validation | 7 | 7 | 100% |
| Benefit Claims Workflow | 7 | 7 | 97% |
| Audit Service | 6 | 6 | 100% |
| Identity & Biometric | 4 | 4 | 100% |
| Integration Gateway | 5 | 5 | 94% |
| Core / RBAC | 6 | 6 | 100% |
| **TOTAL** | **43** | **43** | **99%** |

Continuous integration runs the suite on every push (see the badge above).
