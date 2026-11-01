"""Application configuration for Thiran AI.

Loads settings from environment variables (optionally via a local ``.env``
file) and exposes them through a small, typed ``Settings`` object.

This module is intentionally logic-light: it only reads configuration and
applies sensible defaults. The default AI provider is ``mock`` so the app can
be built and tested without a Gemini API key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

# Load variables from a local ".env" file if present. Values already set in
# the real environment take precedence and are not overridden.
load_dotenv()

# Supported values for configuration fields, kept here so callers can validate
# against a single source of truth.
VALID_AI_PROVIDERS = ("mock", "gemini")
VALID_LANGUAGES = ("english", "tamil", "tanglish")

_DEFAULT_AI_PROVIDER = "mock"
_DEFAULT_DB_PATH = "data/thiran.db"
_DEFAULT_LANGUAGE = "english"


@dataclass(frozen=True)
class Settings:
    """Resolved application settings.

    Attributes:
        ai_provider: Which AI backend to use ("mock" or "gemini").
        gemini_api_key: API key for Gemini; empty until one is provided.
        db_path: Filesystem path to the SQLite database.
        default_language: Default UI language ("english", "tamil", "tanglish").
    """

    ai_provider: str
    gemini_api_key: str
    db_path: str
    default_language: str


def _normalize(value: str) -> str:
    return value.strip().lower()


def _resolve_choice(raw: str, valid: tuple[str, ...], default: str) -> str:
    """Return a normalized choice, falling back to ``default`` if invalid."""
    candidate = _normalize(raw) if raw else ""
    return candidate if candidate in valid else default


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build and cache the :class:`Settings` for the current environment.

    The result is cached so repeated calls are cheap and consistent within a
    single process run.
    """
    ai_provider = _resolve_choice(
        os.getenv("AI_PROVIDER", ""), VALID_AI_PROVIDERS, _DEFAULT_AI_PROVIDER
    )
    default_language = _resolve_choice(
        os.getenv("DEFAULT_LANGUAGE", ""), VALID_LANGUAGES, _DEFAULT_LANGUAGE
    )
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    db_path = os.getenv("DB_PATH", "").strip() or _DEFAULT_DB_PATH

    return Settings(
        ai_provider=ai_provider,
        gemini_api_key=gemini_api_key,
        db_path=db_path,
        default_language=default_language,
    )
