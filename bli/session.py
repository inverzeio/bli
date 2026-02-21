"""Session management — detonation logic and result tracking."""

from __future__ import annotations

import asyncio
import webbrowser
from datetime import datetime, timezone
from typing import Optional

import httpx
from pydantic import BaseModel, HttpUrl

from .client import BrowserlingClient, BrowserlingClientError


SUPPORTED_BROWSERS = ("chrome", "firefox", "edge", "ie")
SUPPORTED_OSES = ("windows", "macos", "linux")


class DetonationResult(BaseModel):
    url: str
    browser: str
    browser_version: str
    os_name: str
    os_version: str
    session_token: str = ""
    session_url: Optional[HttpUrl] = None
    detonated_at: datetime = None  # set in model_post_init
    error: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context: object) -> None:
        if self.detonated_at is None:
            object.__setattr__(self, "detonated_at", datetime.now(timezone.utc))

    @property
    def success(self) -> bool:
        return self.error is None

    def session_url_str(self) -> str:
        return str(self.session_url) if self.session_url else ""


class DetonationSession:
    """Manages the lifecycle of Browserling URL detonations."""

    def __init__(self, client: BrowserlingClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Synchronous single detonation
    # ------------------------------------------------------------------

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
        """Submit a URL for detonation in a sandboxed Browserling session."""
        _validate(browser=browser, os_name=os_name)

        session_token = ""
        session_url = None
        error = None

        try:
            token = self._client.request_session_token(
                url=url,
                browser=browser,
                browser_version=browser_version,
                os_name=os_name,
                os_version=os_version,
            )
            session_token = token.token
            session_url = token.session_url
        except BrowserlingClientError as exc:
            error = str(exc)

        result = DetonationResult(
            url=url,
            browser=browser,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
            session_token=session_token,
            session_url=session_url,
            error=error,
        )

        if result.success and open_locally:
            webbrowser.open(result.session_url_str())

        return result

    # ------------------------------------------------------------------
    # Async concurrent batch detonation
    # ------------------------------------------------------------------

    async def detonate_batch_async(
        self,
        urls: list[str],
        *,
        browser: str = "chrome",
        browser_version: str = "latest",
        os_name: str = "windows",
        os_version: str = "10",
        open_locally: bool = True,
    ) -> list[DetonationResult]:
        """Detonate multiple URLs concurrently using asyncio.

        All session token requests are fired in parallel via a shared
        ``httpx.AsyncClient``. Results are returned in the same order
        as the input ``urls`` list.
        """
        _validate(browser=browser, os_name=os_name)

        async with httpx.AsyncClient(timeout=self._client.config.timeout) as http:
            tasks = [
                self._detonate_one_async(
                    url,
                    browser=browser,
                    browser_version=browser_version,
                    os_name=os_name,
                    os_version=os_version,
                    http=http,
                )
                for url in urls
            ]
            results: list[DetonationResult] = await asyncio.gather(*tasks)

        if open_locally:
            for r in results:
                if r.success:
                    webbrowser.open(r.session_url_str())

        return list(results)

    async def _detonate_one_async(
        self,
        url: str,
        *,
        browser: str,
        browser_version: str,
        os_name: str,
        os_version: str,
        http: httpx.AsyncClient,
    ) -> DetonationResult:
        session_token = ""
        session_url = None
        error = None

        try:
            token = await self._client.request_session_token_async(
                url=url,
                browser=browser,
                browser_version=browser_version,
                os_name=os_name,
                os_version=os_version,
                http=http,
            )
            session_token = token.token
            session_url = token.session_url
        except BrowserlingClientError as exc:
            error = str(exc)

        return DetonationResult(
            url=url,
            browser=browser,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
            session_token=session_token,
            session_url=session_url,
            error=error,
        )


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
