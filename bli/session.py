"""Session management — detonation logic and result tracking."""

from __future__ import annotations

import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .client import BrowserlingClient, BrowserlingClientError, SessionToken


# Browsers and OSes Browserling supports.
SUPPORTED_BROWSERS = ("chrome", "firefox", "edge", "ie")
SUPPORTED_OSES = ("windows", "macos", "linux")


@dataclass
class DetonationResult:
    url: str
    browser: str
    browser_version: str
    os_name: str
    os_version: str
    session_token: str
    session_url: str
    detonated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None


class DetonationSession:
    """Manages the lifecycle of a Browserling URL detonation."""

    def __init__(self, client: BrowserlingClient) -> None:
        self._client = client

    def detonate(
        self,
        url: str,
        *,
        browser: str = "chrome",
        browser_version: str = "latest",
        os_name: str = "windows",
        os_version: str = "10",
        open_locally: bool = True,
    ) -> DetonationResult:
        """Submit a URL for detonation in a sandboxed Browserling session.

        Parameters
        ----------
        url:
            The suspicious URL to open.
        browser:
            Browser to use. One of: ``chrome``, ``firefox``, ``edge``, ``ie``.
        browser_version:
            Browser version (e.g. ``"latest"`` or ``"11"`` for IE 11).
        os_name:
            Operating system. One of: ``windows``, ``macos``, ``linux``.
        os_version:
            OS version string (e.g. ``"10"`` for Windows 10).
        open_locally:
            If ``True``, open the session URL in the analyst's local browser
            so they can observe the detonation in real time.

        Returns
        -------
        DetonationResult
        """
        self._validate(browser=browser, os_name=os_name)

        token: Optional[SessionToken] = None
        error: Optional[str] = None

        try:
            token = self._client.request_session_token(
                url=url,
                browser=browser,
                browser_version=browser_version,
                os_name=os_name,
                os_version=os_version,
            )
        except BrowserlingClientError as exc:
            error = str(exc)

        result = DetonationResult(
            url=url,
            browser=browser,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
            session_token=token.token if token else "",
            session_url=token.session_url if token else "",
            error=error,
        )

        if result.success and open_locally:
            webbrowser.open(result.session_url)

        return result

    def detonate_batch(
        self,
        urls: list[str],
        *,
        browser: str = "chrome",
        browser_version: str = "latest",
        os_name: str = "windows",
        os_version: str = "10",
        open_locally: bool = True,
    ) -> list[DetonationResult]:
        """Detonate multiple URLs sequentially."""
        return [
            self.detonate(
                url,
                browser=browser,
                browser_version=browser_version,
                os_name=os_name,
                os_version=os_version,
                open_locally=open_locally,
            )
            for url in urls
        ]

    @staticmethod
    def _validate(*, browser: str, os_name: str) -> None:
        if browser not in SUPPORTED_BROWSERS:
            raise ValueError(
                f"Unsupported browser '{browser}'. "
                f"Choose from: {', '.join(SUPPORTED_BROWSERS)}"
            )
        if os_name not in SUPPORTED_OSES:
            raise ValueError(
                f"Unsupported OS '{os_name}'. "
                f"Choose from: {', '.join(SUPPORTED_OSES)}"
            )
