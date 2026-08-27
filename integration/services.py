"""Integration Gateway resilience patterns: retry-with-backoff and circuit breaker."""

class CircuitBreakerOpen(Exception):
    pass

def retry_with_backoff(fn, retries=3, base_delay=0, sleep=None):
    last = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            if sleep and base_delay:
                sleep(base_delay * (2 ** attempt))
    raise last

class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"

    def __init__(self, threshold=3):
        self.threshold = threshold
        self.failures = 0
        self.state = self.CLOSED

    def call(self, fn):
        if self.state == self.OPEN:
            raise CircuitBreakerOpen("Circuit is open")
        try:
            result = fn()
        except Exception:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = self.OPEN
            raise
        self.failures = 0
        self.state = self.CLOSED
        return result

    def half_open(self):
        self.state = self.HALF_OPEN
