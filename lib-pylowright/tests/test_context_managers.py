from typing import Any

from pylowright.browser.browser import Browser
from pylowright.browser.session import BrowserSession, _Mode


class PageStub:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class ContextStub:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class SessionStub(BrowserSession):
    def __init__(self) -> None:
        self._mode = _Mode.EPHEMERAL
        self._page = PageStub()
        self._context = ContextStub()
        self._playwright = None
        self._tracing_active = False
        self.close_called = False

    def close(self) -> None:
        self.close_called = True
        super().close()


def test_browser_context_manager_closes_on_exit():
    with Browser(SessionStub()) as browser:
        assert browser.session is not None

    assert browser.session.close_called


def test_session_context_manager_closes_resources():
    session = SessionStub()
    with session as sess:
        assert sess is session

    assert session._context.closed
    assert session.close_called
