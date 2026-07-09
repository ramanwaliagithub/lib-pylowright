"""Browser configuration dataclasses."""

from dataclasses import dataclass, field
from typing import Literal

BrowserType = Literal["chromium", "firefox", "webkit"]


@dataclass
class ProcessConfig:
    """Args for Browser.launch()"""
    headless: bool = True
    channel: str | None = None
    args: list[str] = field(default_factory=list)
    executable_path: str | None = None
    timeout: int | None = None
    downloads_path: str | None = None


@dataclass
class SessionConfig:
    """Args for Browser.new_context()"""
    viewport: dict[str, int] | None = None
    ignore_https_errors: bool = True
    accept_downloads: bool = True
    user_agent: str | None = None


@dataclass
class BrowserProfile:
    name: str
    browser_type: BrowserType
    process: ProcessConfig
    session: SessionConfig
    user_data_dir: str | None = None
