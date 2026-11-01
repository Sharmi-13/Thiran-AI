"""Model factory: the single swap-point between mock and Gemini backends.

Agents obtain their Strands ``Model`` from here, so switching providers later
is a one-line change driven by ``AI_PROVIDER`` in configuration.
"""

from __future__ import annotations

from typing import Optional

from strands.models import Model

from utils.config import Settings, get_settings

from .mock_model import MockModel


def get_model(settings: Optional[Settings] = None) -> Model:
    """Return a Strands ``Model`` for the configured AI provider.

    Args:
        settings: Optional resolved settings; defaults to ``get_settings()``.

    Returns:
        A ready-to-use Strands model instance.

    Raises:
        NotImplementedError: If ``AI_PROVIDER`` is "gemini", which is not yet
            implemented. Set ``AI_PROVIDER=mock`` to build and test now.
        ValueError: If ``AI_PROVIDER`` is an unrecognized value.
    """
    settings = settings or get_settings()
    provider = settings.ai_provider

    if provider == "mock":
        return MockModel(language=settings.default_language)

    if provider == "gemini":
        raise NotImplementedError(
            "Gemini provider is not implemented yet. Set AI_PROVIDER=mock to "
            "build and test with the mock model."
        )

    raise ValueError(f"Unknown AI_PROVIDER: {provider!r}")
