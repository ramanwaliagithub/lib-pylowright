from typing import Any

from pylowright.browser.browser import Browser
from pylowright.browser.session import BrowserSession, _Mode


class FakePage:
    def __init__(self) -> None:
        self.goto_calls = []
        self.wait_calls = []
        self._title = "Example"
        self._url = "about:blank"

    def goto(self, url: str, wait_until: str = "load") -> None:
        self.goto_calls.append((url, wait_until))
        self._url = url

    def wait_for_load_state(self, state: str = "load") -> None:
        self.wait_calls.append(state)

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url


class FakeSession(BrowserSession):
    def __init__(self) -> None:
        self._mode = _Mode.EPHEMERAL
        self._page = FakePage()
        self._context = None
        self._playwright = None
        self.actions = []

    def restart_context(self) -> None:
        self.actions.append("restart_context")

    def restart_page(self) -> None:
        self.actions.append("restart_page")

    def restart_persistent(self) -> None:
        self.actions.append("restart_persistent")

    def update_external_context(self, pw_context: Any) -> None:
        self.actions.append(("update_external_context", pw_context))

    def start_tracing(self, screenshots: bool = True, snapshots: bool = True,
                      sources: bool = True) -> None:
        self.actions.append(("start_tracing", screenshots, snapshots, sources))

    def stop_tracing(self, trace_path: str | None = None) -> None:
        self.actions.append(("stop_tracing", trace_path))


def test_browser_wrapper_forwards_page_methods():
    session = FakeSession()
    browser = Browser(session)

    browser.goto("https://example.com")
    browser.wait_for_load_state("networkidle")

    assert browser.title == "Example"
    assert browser.url == "https://example.com"
    assert browser.page.goto_calls == [("https://example.com", "load")]
    assert browser.page.wait_calls == ["networkidle"]


def test_browser_wrapper_forwards_lifecycle_methods():
    session = FakeSession()
    browser = Browser(session)

    browser.restart_context()
    browser.restart_page()
    browser.restart_persistent()
    browser.update_external_context("fake-context")
    browser.start_tracing(screenshots=False, snapshots=False, sources=False)
    browser.stop_tracing("/tmp/trace.zip")

    assert session.actions == [
        "restart_context",
        "restart_page",
        "restart_persistent",
        ("update_external_context", "fake-context"),
        ("start_tracing", False, False, False),
        ("stop_tracing", "/tmp/trace.zip"),
    ]
