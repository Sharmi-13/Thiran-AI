"""Model factory: the single swap-point between mock and Gemini backends.

Agents obtain their Strands ``Model`` from here, so switching providers is a
one-line change driven by ``AI_PROVIDER`` in configuration.

Security note: the Gemini API key is read from the ``GEMINI_API_KEY``
environment variable and passed directly into the model client. It is never
logged, printed, or written anywhere by this module.
"""

from __future__ import annotations

import os
from typing import Optional

from strands.models import Model

from utils.config import Settings, get_settings

from .mock_model import MockModel

# Default Gemini model id when GEMINI_MODEL is not set.
DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"


def get_model(settings: Optional[Settings] = None) -> Model:
    """Return a Strands ``Model`` for the configured AI provider.

    Args:
        settings: Optional resolved settings; defaults to ``get_settings()``.

    Returns:
        A ready-to-use Strands model instance.

    Raises:
        RuntimeError: If ``AI_PROVIDER`` is "gemini" but ``GEMINI_API_KEY`` is
            not set.
        ValueError: If ``AI_PROVIDER`` is an unrecognized value.
    """
    settings = settings or get_settings()
    provider = settings.ai_provider

    if provider == "mock":
        return MockModel(language=settings.default_language)

    if provider == "gemini":
        return _build_gemini_model()

    raise ValueError(f"Unknown AI_PROVIDER: {provider!r}")


def _build_gemini_model() -> Model:
    """Construct the built-in Strands ``GeminiModel``.

    The API key is read from ``GEMINI_API_KEY`` and handed straight to the
    client via ``client_args``; it is not stored on any named attribute here,
    logged, or printed. The model id comes from ``GEMINI_MODEL`` (default
    :data:`DEFAULT_GEMINI_MODEL`).
    """
    # Imported lazily so the mock path has no dependency on the gemini extra.
    from google.genai.types import HttpOptions, HttpRetryOptions, ThinkingConfig
    from strands.models.gemini import GeminiModel

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "AI_PROVIDER=gemini but GEMINI_API_KEY is not set. Add it to your "
            ".env file."
        )

    model_id = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL

    # Fail fast instead of hanging: 90s request timeout (milliseconds) and at
    # most one retry (attempts counts the original request, so 2 == 1 retry).
    http_options = HttpOptions(
        timeout=90_000,
        retry_options=HttpRetryOptions(attempts=2),
    )

    # Keep a small thinking budget so responses return faster. The provider
    # forwards params into GenerateContentConfig, so thinking_config applies.
    return GeminiModel(
        client_args={"api_key": os.environ["GEMINI_API_KEY"], "http_options": http_options},
        model_id=model_id,
        params={"thinking_config": ThinkingConfig(thinking_budget=128)},
    )
