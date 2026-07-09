"""Compatibility browser API similar to pylonium's browser module."""

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
