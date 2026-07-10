"""Compatibility browser API with lightweight session management."""

from typing import Any

from pylowright.browser.factory import get_profile_name
from pylowright.browser.lifecycle import (
    close_browser,
    close_persistent_browser,
    get_profile,
    start_browser,
    start_persistent_browser,
)
from pylowright.browser.session import BrowserSession

__all__ = [
    "Browser",
    "BrowserSession",
    "close_browser",
    "close_persistent_browser",
    "get_profile",
    "get_profile_name",
    "start_browser",
    "start_persistent_browser",
]


class Browser:
    """Lightweight compatibility wrapper around BrowserSession."""

    def __init__(self, session: BrowserSession | None = None) -> None:
        self.session = session or BrowserSession.deferred()

    @classmethod
    def persistent(cls, profile: str | None = None, **overrides: Any) -> "Browser":
        session = BrowserSession.persistent(profile, **overrides)
        return cls(session)

    @classmethod
    def ephemeral(cls, pw_browser: Any, profile: str | None = None, **overrides: Any) -> "Browser":
        session = BrowserSession.ephemeral(pw_browser, profile, **overrides)
        return cls(session)

    def activate_external(self, pw_context: Any) -> None:
        self.session.activate_external(pw_context)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "Browser":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @property
    def page(self) -> Any:
        return self.session.page

    @property
    def context(self) -> Any:
        return self.session.context

    def goto(self, url: str, wait_until: str = "load") -> None:
        self.session.goto(url, wait_until=wait_until)

    def wait_for_load_state(self, state: str = "load") -> None:
        self.session.wait_for_load_state(state)

    def restart_context(self) -> None:
        self.session.restart_context()

    def restart_page(self) -> None:
        self.session.restart_page()

    def restart_persistent(self) -> None:
        self.session.restart_persistent()

    def update_external_context(self, pw_context: Any) -> None:
        self.session.update_external_context(pw_context)

    def start_tracing(self, screenshots: bool = True, snapshots: bool = True,
                      sources: bool = True) -> None:
        self.session.start_tracing(screenshots=screenshots, snapshots=snapshots,
                                   sources=sources)

    def stop_tracing(self, trace_path: str | None = None) -> None:
        self.session.stop_tracing(trace_path=trace_path)

    @property
    def title(self) -> str:
        return self.session.title

    @property
    def url(self) -> str:
        return self.session.url
