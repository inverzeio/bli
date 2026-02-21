"""Browserling Live API client — handles session token requests."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, HttpUrl, field_validator

from .config import BrowserlingConfig

BROWSERLING_SESSION_ENDPOINT = "https://www.browserling.com/liveapi_v1_session"


class SessionToken(BaseModel):
    token: str
    session_url: HttpUrl

    @field_validator("token")
    @classmethod
    def token_must_not_be_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("token must not be empty")
        return v


class BrowserlingClientError(Exception):
    pass


class BrowserlingAuthError(BrowserlingClientError):
    pass


class BrowserlingClient:
    """Thin client for the Browserling Live API."""

    def __init__(self, config: BrowserlingConfig | None = None) -> None:
        self.config = config or BrowserlingConfig()

    def _auth_headers(self) -> dict[str, str]:
        return {"Browserling-Api-Key": self.config.api_key.get_secret_value()}

    def _build_params(
        self,
        *,
        url: str,
        browser: str,
        browser_version: str,
        os_name: str,
        os_version: str,
    ) -> dict[str, str]:
        return {
            "url": url,
            "browser": browser,
            "browser_version": browser_version,
            "os": os_name,
            "os_version": os_version,
        }

    def request_session_token(
        self,
        *,
        url: str,
        browser: str = "chrome",
        browser_version: str = "latest",
        os_name: str = "windows",
        os_version: str = "10",
    ) -> SessionToken:
        """Request a one-time session token (synchronous)."""
        params = self._build_params(
            url=url,
            browser=browser,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
        )
        try:
            with httpx.Client(timeout=self.config.timeout) as http:
                response = http.get(
                    BROWSERLING_SESSION_ENDPOINT,
                    params=params,
                    headers=self._auth_headers(),
                )
        except httpx.TransportError as exc:
            raise BrowserlingClientError(
                f"Network error contacting Browserling: {exc}"
            ) from exc

        return self._parse(response)

    async def request_session_token_async(
        self,
        *,
        url: str,
        browser: str = "chrome",
        browser_version: str = "latest",
        os_name: str = "windows",
        os_version: str = "10",
        http: httpx.AsyncClient,
    ) -> SessionToken:
        """Request a one-time session token (asynchronous).

        The caller is responsible for providing (and closing) the
        ``httpx.AsyncClient`` so that a single client can be reused
        across concurrent requests in a batch.
        """
        params = self._build_params(
            url=url,
            browser=browser,
            browser_version=browser_version,
            os_name=os_name,
            os_version=os_version,
        )
        try:
            response = await http.get(
                BROWSERLING_SESSION_ENDPOINT,
                params=params,
                headers=self._auth_headers(),
            )
        except httpx.TransportError as exc:
            raise BrowserlingClientError(
                f"Network error contacting Browserling: {exc}"
            ) from exc

        return self._parse(response)

    def _parse(self, response: httpx.Response) -> SessionToken:
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
        try:
            data = response.json()
        except Exception as exc:
            raise BrowserlingClientError(
                f"Could not parse Browserling response as JSON: {response.text[:200]}"
            ) from exc

        try:
            return SessionToken.model_validate(data)
        except Exception as exc:
            raise BrowserlingClientError(
                f"Unexpected response shape from Browserling: {data}"
            ) from exc
