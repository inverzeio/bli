"""Settings loaded from environment variables / .env file."""

from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BrowserlingConfig(BaseSettings):
    """Application configuration.

    Values are read from environment variables (or a ``.env`` file).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BROWSERLING_",
        # BROWSERLING_API_KEY, BROWSERLING_DEFAULT_BROWSER, etc.
    )

    api_key: SecretStr = SecretStr("")
    """Browserling Live API key. Required."""

    default_browser: str = "chrome"
    default_os: str = "windows"
    timeout: float = 15.0

    def validate_api_key(self) -> None:
        if not self.api_key.get_secret_value():
            raise ValueError(
                "BROWSERLING_API_KEY is not set. "
                "Add it to your .env file or export it as an environment variable."
            )
