import os
from pathlib import Path

T_TIMEOUT_SHORT = int(os.getenv("PW_TIMEOUT_SHORT", "5"))
T_TIMEOUT_DEFAULT = int(os.getenv("PW_TIMEOUT_DEFAULT", "30"))
T_TIMEOUT_LONG = int(os.getenv("PW_TIMEOUT_LONG", "120"))

__version__ = Path(__file__).with_name("version.txt").read_text().strip()

from pylowright.browser import (
    Browser,
    BrowserSession,
    close_browser,
    close_persistent_browser,
    get_profile,
    get_profile_name,
    start_browser,
    start_persistent_browser,
)

__all__ = [
    "Browser",
    "BrowserSession",
    "close_browser",
    "close_persistent_browser",
    "get_profile",
    "get_profile_name",
    "start_browser",
    "start_persistent_browser",
    "__version__",
    "T_TIMEOUT_DEFAULT",
    "T_TIMEOUT_LONG",
    "T_TIMEOUT_SHORT",
]
