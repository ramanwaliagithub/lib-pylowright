from typing import Any

from pylowright.browser.browser import Browser
from pylowright.browser.session import BrowserSession, _Mode


class FakePage:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeContext:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeSession(BrowserSession):
    def __init__(self) -> None:
        self._mode = _Mode.EPHEMERAL
        self._page = FakePage()
        self._context = FakeContext()
        self._playwright = None
        self._tracing_active = False
        self.close_called = False

    def close(self) -> None:
        self.close_called = True
        super().close()


def test_browser_context_manager_closes_on_exit():
    with Browser(FakeSession()) as browser:
        assert browser.session is not None

    assert browser.session.close_called


def test_session_context_manager_closes_resources():
    session = FakeSession()
    with session as sess:
        assert sess is session

    assert session._context.closed
    assert session.close_called
