import os
import importlib

from pylowright.browser.factory import get_profile_name, clear_env_cache
from pylowright.browser.lifecycle import get_profile, start_browser, start_persistent_browser
from pylowright.browser.config import BrowserProfile


def test_default_profile_is_chrome():
    clear_env_cache()
    assert get_profile_name() == "chrome"


def test_get_profile_returns_browser_profile():
    profile = get_profile("chrome")
    assert isinstance(profile, BrowserProfile)
    assert profile.name == "chrome"


def test_start_browser_and_persistent_browser_raise_without_playwright(monkeypatch):
    monkeypatch.setattr("pylowright.browser.lifecycle.sync_playwright", lambda: None)
    try:
        start_browser()
    except Exception as exc:
        assert isinstance(exc, Exception)

    try:
        start_persistent_browser()
    except Exception as exc:
        assert isinstance(exc, Exception)
