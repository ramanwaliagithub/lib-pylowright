"""Pylowright browser module - simplified architecture with procedural lifecycle."""

from pylowright.browser.browser import Browser
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
