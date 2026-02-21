"""Browserling Live API client — handles session token requests."""

from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

BROWSERLING_SESSION_ENDPOINT = "https://www.browserling.com/liveapi_v1_session"
API_KEY_ENV = "BROWSERLING_API_KEY"


@dataclass
class SessionToken:
    token: str
    session_url: str


class BrowserlingClientError(Exception):
    pass


class BrowserlingAuthError(BrowserlingClientError):
    pass


class BrowserlingClient:
    """Thin client for the Browserling Live API."""

    def __init__(self, api_key: str | None = None, timeout: float = 15.0) -> None:
        self.api_key = api_key or os.environ.get(API_KEY_ENV)
        if not self.api_key:
            raise BrowserlingAuthError(
                f"No API key found. Set the {API_KEY_ENV} environment variable "
                "or pass api_key= explicitly."
            )
        self._timeout = timeout

    def request_session_token(
        self,
        *,
        url: str,
        browser: str = "chrome",
        browser_version: str = "latest",
        os_name: str = "windows",
        os_version: str = "10",
    ) -> SessionToken:
        """Request a one-time session token from Browserling.

        Parameters
        ----------
        url:
            The target URL to open inside the sandboxed browser.
        browser:
            Browser to use: ``chrome``, ``firefox``, ``edge``, ``ie``.
        browser_version:
            Browser version string, e.g. ``"latest"`` or ``"11"`` for IE 11.
        os_name:
            Operating system: ``windows``, ``macos``, ``linux``.
        os_version:
            OS version string, e.g. ``"10"`` for Windows 10.

        Returns
        -------
        SessionToken
            A dataclass containing the one-time token and the ready-to-use
            session URL.

        Raises
        ------
        BrowserlingAuthError
            When the API key is rejected (HTTP 401/403).
        BrowserlingClientError
            For any other API or network failure.
        """
        params = {
            "url": url,
            "browser": browser,
            "browser_version": browser_version,
            "os": os_name,
            "os_version": os_version,
        }
        headers = {"Browserling-Api-Key": self.api_key}

        try:
            with httpx.Client(timeout=self._timeout) as http:
                response = http.get(
                    BROWSERLING_SESSION_ENDPOINT,
                    params=params,
                    headers=headers,
                )
        except httpx.TransportError as exc:
            raise BrowserlingClientError(
                f"Network error contacting Browserling: {exc}"
            ) from exc

        if response.status_code in (401, 403):
            raise BrowserlingAuthError(
                f"Browserling rejected the API key (HTTP {response.status_code}). "
                "Check your BROWSERLING_API_KEY."
            )

        if response.status_code != 200:
            raise BrowserlingClientError(
                f"Unexpected HTTP {response.status_code} from Browserling: "
                f"{response.text[:200]}"
            )

        data = self._parse_response(response)
        return SessionToken(
            token=data["token"],
            session_url=data["session_url"],
        )

    @staticmethod
    def _parse_response(response: httpx.Response) -> dict:
        try:
            data = response.json()
        except Exception as exc:
            raise BrowserlingClientError(
                f"Could not parse Browserling response as JSON: {response.text[:200]}"
            ) from exc

        if "token" not in data or "session_url" not in data:
            raise BrowserlingClientError(
                f"Unexpected response shape from Browserling: {data}"
            )

        return data
