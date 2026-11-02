"""Shared helpers for the Thiran AI agents.

Keeps role labels and small utilities in one place so the three agents stay
consistent. Each agent builds a real ``strands.Agent`` with a model obtained
from :func:`ai.factory.get_model`, so the backend (Gemini or mock) is chosen
by configuration, not by the agents themselves.
"""

from __future__ import annotations

# Human-readable labels for the supported roles. Keys are stable identifiers;
# values are injected into agent prompts.
ROLE_LABELS = {
    "software": "Software Developer / IT",
    "data_analyst": "Data Analyst",
    "customer_support": "Customer Support",
    "business_marketing": "Business / Marketing",
}

DEFAULT_ROLE = "software"


def role_label(role: str | None) -> str:
    """Return a human-readable label for a role identifier.

    Falls back to the default role label for unknown or missing input so
    prompt construction never fails.
    """
    if not role:
        return ROLE_LABELS[DEFAULT_ROLE]
    return ROLE_LABELS.get(role.strip().lower(), ROLE_LABELS[DEFAULT_ROLE])
