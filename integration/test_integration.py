import pytest
from integration.services import retry_with_backoff, CircuitBreaker, CircuitBreakerOpen

def test_retry_succeeds_after_transient_failures():
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("transient")
        return "ok"
    assert retry_with_backoff(flaky, retries=3) == "ok"
    assert calls["n"] == 3

def test_retry_exhausts_and_raises():
    def always_fail():
        raise RuntimeError("down")
    with pytest.raises(RuntimeError):
        retry_with_backoff(always_fail, retries=2)

def test_circuit_opens_after_threshold():
    cb = CircuitBreaker(threshold=3)
    def fail():
        raise RuntimeError("x")
    for _ in range(3):
        with pytest.raises(RuntimeError):
            cb.call(fail)
    assert cb.state == CircuitBreaker.OPEN

def test_open_circuit_raises_circuitbreakeropen():
    cb = CircuitBreaker(threshold=1)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
    with pytest.raises(CircuitBreakerOpen):
        cb.call(lambda: "never")

def test_success_resets_failures():
    cb = CircuitBreaker(threshold=3)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
    cb.call(lambda: "ok")
    assert cb.failures == 0 and cb.state == CircuitBreaker.CLOSED
