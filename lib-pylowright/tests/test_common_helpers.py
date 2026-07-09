from pylowright.common.logger import setup_logging
from pylowright.common.retry import retry


def test_retry_decorator_accepts_simple_callable():
    calls = {"count": 0}

    @retry(timeout_s=1, polling_ms=10)
    def flaky_success() -> bool:
        calls["count"] += 1
        return calls["count"] >= 2

    assert flaky_success() is True
    assert calls["count"] >= 2


def test_setup_logging_does_not_raise():
    setup_logging("pylowright.test")
