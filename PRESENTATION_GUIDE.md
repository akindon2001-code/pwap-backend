# Defence demo — 3-minute runbook

Present from a terminal with the virtual environment already activated.

## Before the session
    unzip PWAP_Backend_Presentation.zip && cd pwap_backend
    python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    pytest -q            # confirm 43 passed on this machine

## During the defence (say this, run that)

1. "The backend logic is covered by an automated suite — here it is running."
       pytest --cov --cov-report=term-missing
   -> point at: 43 passed, TOTAL 99%.

2. "And the coverage report, module by module."
       coverage html && open htmlcov/index.html        # Windows: start htmlcov\index.html
   -> open in browser, scroll the module list.

3. "Here is the system's core logic working end to end."
       python demo.py
   -> narrate: remittance validation catches all four exception types;
      the claim moves through its seven stages; the audit trail is
      hash-verified and detects a forged record.

4. "It's on GitHub and CI runs on every push." -> show the repo + green CI badge.

## The one honest line to have ready
"This is a tested, runnable reference implementation of the core backend
logic — not the full production system with Oracle, Camunda and live PenCom
integration. Everything I've shown is genuinely running and reproducible."
