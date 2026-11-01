"""Thiran AI model-provider package.

Exposes the custom Strands mock model and the provider factory. The three
agents consume a Strands ``Model`` from :func:`ai.factory.get_model`, keeping
the backend swappable (mock now, Gemini later) without touching agent code.
"""

from .factory import get_model
from .mock_model import MockModel

__all__ = ["get_model", "MockModel"]
