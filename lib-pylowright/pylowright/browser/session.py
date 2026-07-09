"""BrowserSession - Persistent browser session managing context + page lifecycle."""

import contextlib
import logging
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser as PlaywrightBrowser
from playwright.sync_api import BrowserContext, Page, Playwright

from pylowright.browser.lifecycle import (
    close_persistent_browser,
    get_profile,
    start_persistent_browser,
)
from pylowright.common.logger import autolog

logger = logging.getLogger(__name__)


class _Mode(str, Enum):
    """Operating modes for BrowserSession."""

    DEFERRED = "deferred"
    EPHEMERAL = "ephemeral"
    PERSISTENT = "persistent"
    EXTERNAL = "external"


class BrowserSession:  # pylint: disable=too-many-instance-attributes
    """Persistent object managing context + page lifecycle.

    Key: Object persists while .page and .context properties stay current.
    PageObjects survive restarts without reinitialization.
    """

    def _init_empty(self) -> None:
        """Initialize all attributes to None/defaults (deferred state)."""
        self._playwright: Playwright | None = None
        self._browser: PlaywrightBrowser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._mode = _Mode.DEFERRED
        self._config: dict[str, Any] = {}
        self._restart_profile: str | None = None
        self._restart_overrides: dict[str, Any] | None = None
        self._tracing_active = False

    def _require_active(self) -> None:
        """Raise if session is not yet activated."""
        if self._mode == _Mode.DEFERRED:
            raise RuntimeError("Session not activated — call activate_*() first")

    def _require_deferred(self) -> None:
        """Raise if session is not in deferred state (already activated)."""
        if self._mode != _Mode.DEFERRED:
            msg = (
                f"Session already activated (mode={self._mode.value})"
                " — activate_*() only for deferred sessions"
            )
            raise RuntimeError(msg)

    def _discard_tracing(self) -> None:
        """Stop active tracing, discarding data. No-op if inactive or no context."""
        if not self._tracing_active:
            return
        if self._context:
            logger.warning("Discarding active trace — stop tracing before restart/update")
            with contextlib.suppress(Exception):
                self._context.tracing.stop()
        self._tracing_active = False

    @autolog(logger)
    def __init__(self, pw_browser: PlaywrightBrowser,
                 profile: str | None = None, **overrides: Any) -> None:
        self._init_empty()
        self.activate_ephemeral(pw_browser, profile, **overrides)

    @autolog(logger)
    def activate_ephemeral(self, pw_browser: PlaywrightBrowser,
                           profile: str | None = None, **overrides: Any) -> None:
        """Wire deferred session to a real browser (ephemeral multi-context mode)."""
        self._require_deferred()
        profile_obj = get_profile(profile)
        base_config = asdict(profile_obj.session)
        self._config = {**base_config, **overrides}
        self._browser = pw_browser
        self._context = pw_browser.new_context(**self._config)
        self._page = self._context.new_page()
        self._mode = _Mode.EPHEMERAL
        logger.debug("Session activated (ephemeral, profile=%s): %s",
                      profile_obj.name, self._config)

    @autolog(logger)
    def activate_persistent(self, profile: str | None = None,
                            **overrides: Any) -> None:
        """Wire deferred session to a new persistent browser (manages Playwright internally)."""
        self._require_deferred()
        profile_name = get_profile(profile).name
        pw, pw_context = start_persistent_browser(profile_name, **overrides)
        self._playwright = pw
        self._context = pw_context
        self._page = pw_context.pages[0] if pw_context.pages else pw_context.new_page()
        self._mode = _Mode.PERSISTENT
        self._restart_profile = profile_name
        self._restart_overrides = overrides
        logger.debug("Session activated (persistent, profile=%s, overrides=%s)",
                      profile_name, overrides)

    @autolog(logger)
    def activate_external(self, pw_context: BrowserContext) -> None:
        """Wire deferred session to a user-created context.

        User manages Playwright + context lifecycle.
        Only restart_page() and update_external_context() supported.
        """
        self._require_deferred()
        self._context = pw_context
        self._page = pw_context.pages[0] if pw_context.pages else pw_context.new_page()
        self._mode = _Mode.EXTERNAL
        logger.debug("Session activated (external, user-managed context)")

    @classmethod
    def deferred(cls) -> "BrowserSession":
        """Create placeholder session — call activate_*() later to wire Playwright objects.

        Useful when session must exist before browser launch (e.g., RobotFramework).
        """
        session = object.__new__(cls)
        session._init_empty()
        logger.debug("Deferred session created")
        return session

    @classmethod
    def ephemeral(
        cls, pw_browser: PlaywrightBrowser,
        profile: str | None = None, **overrides: Any,
    ) -> "BrowserSession":
        """Create ephemeral session (caller manages Playwright + Browser lifecycle)."""
        session = cls.deferred()
        session.activate_ephemeral(pw_browser, profile, **overrides)
        return session

    @classmethod
    def persistent(
        cls, profile: str | None = None, **overrides: Any,
    ) -> "BrowserSession":
        """Create persistent session (manages Playwright instance internally)."""
        session = cls.deferred()
        session.activate_persistent(profile, **overrides)
        return session

    @classmethod
    def external(cls, pw_context: BrowserContext) -> "BrowserSession":
        """Wrap user-created context (persistent or ephemeral).

        User manages Playwright + context lifecycle.
        Only restart_page() and update_external_context() supported.
        """
        session = cls.deferred()
        session.activate_external(pw_context)
        return session

    @property
    def page(self) -> Page:
        """Always current, even after restart."""
        self._require_active()
        assert self._page is not None
        return self._page

    @property
    def context(self) -> BrowserContext:
        """Always current, even after restart."""
        self._require_active()
        assert self._context is not None
        return self._context

    def goto(self, url: str, wait_until: str = "load") -> None:
        """Navigate the current page to the given URL."""
        self.page.goto(url, wait_until=wait_until)

    def wait_for_load_state(self, state: str = "load") -> None:
        """Wait for the current page to reach the requested load state."""
        self.page.wait_for_load_state(state)

    @property
    def title(self) -> str:
        """Return the current page title."""
        return self.page.title

    @property
    def url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    @autolog(logger)
    def restart_context(self) -> None:
        """New context + page (normal mode only)."""
        self._require_active()
        if self._mode == _Mode.PERSISTENT:
            raise RuntimeError("Use restart_persistent() for persistent mode")
        if self._mode == _Mode.EXTERNAL:
            raise RuntimeError("Cannot restart - context was user-created")
        self._discard_tracing()
        if self._context:
            self._context.close()  # closes all pages automatically
        assert self._browser is not None
        self._context = self._browser.new_context(**self._config)
        self._page = self._context.new_page()
        logger.debug("Context restarted (and new page created) with config: %s", self._config)

    @autolog(logger)
    def restart_page(self) -> None:
        """New page, keeps context/cookies.

        Opens the new page before closing the old one so the browser never
        reaches zero tabs — non-headless Chromium in a persistent context
        shuts down when the last tab is closed.
        """
        old_page = self._page
        self._page = self.context.new_page()
        if old_page:
            old_page.close()
        logger.debug("Page restarted (context preserved)")

    @autolog(logger)
    def restart_persistent(self) -> None:
        """Restart persistent browser (persistent factory mode only)."""
        if self._mode != _Mode.PERSISTENT:
            raise RuntimeError("Only for persistent mode")

        assert self._playwright is not None
        assert self._context is not None
        assert self._restart_overrides is not None

        self._discard_tracing()
        close_persistent_browser(self._playwright, self._context)
        pw, pw_context = start_persistent_browser(
            self._restart_profile, **self._restart_overrides)

        self._playwright = pw
        self._context = pw_context
        if pw_context.pages:
            self._page = pw_context.pages[0]
        else:
            self._page = pw_context.new_page()

    @autolog(logger)
    def update_external_context(self, pw_context: BrowserContext) -> None:
        """Update to new user-provided context (external mode only).

        Allows user to recreate context externally while keeping same
        BrowserSession instance for PageObjects.
        """
        if self._mode != _Mode.EXTERNAL:
            raise RuntimeError("update_external_context() only for external mode")

        self._discard_tracing()
        old_page = self._page

        self._context = pw_context
        if pw_context.pages:
            self._page = pw_context.pages[0]
        else:
            self._page = pw_context.new_page()

        # Close old page after new context is wired up (zero-tab safety).
        if old_page:
            old_page.close()

        logger.debug("Context updated (user-managed)")

    @autolog(logger)
    def start_tracing(self, screenshots: bool = True, snapshots: bool = True,
                      sources: bool = True) -> None:
        """Start tracing. Call stop_tracing() with path to save, without to discard."""
        if self._tracing_active:
            logger.warning("Tracing already active")
            return

        self.context.tracing.start(
            screenshots=screenshots, snapshots=snapshots, sources=sources)
        self._tracing_active = True

    @autolog(logger)
    def stop_tracing(self, trace_path: str | None = None) -> None:
        """Stop tracing. Saves to trace_path if provided, discards if None."""
        if not self._tracing_active:
            logger.warning("Tracing not active")
            return

        try:
            if trace_path:
                Path(trace_path).parent.mkdir(parents=True, exist_ok=True)
                self.context.tracing.stop(path=trace_path)
                logger.info("Trace saved to: %s", trace_path)
            else:
                self.context.tracing.stop()
        except Exception:
            logger.exception("Error stopping tracing")

        self._tracing_active = False

    @autolog(logger)
    def close(self) -> None:
        self._discard_tracing()

        # Closes all pages automatically; avoids last-tab-kills-browser in persistent.
        if self._context:
            self._context.close()
        if self._mode == _Mode.PERSISTENT and self._playwright:
            self._playwright.stop()
