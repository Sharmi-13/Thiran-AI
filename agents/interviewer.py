"""Interviewer agent.

A genuine ``strands.Agent`` that asks exactly one English interview question
for a chosen role.
"""

from __future__ import annotations

from collections.abc import Sequence

from strands import Agent

from ai import get_model

from ._common import role_label

SYSTEM_PROMPT = (
    "You are a professional job interviewer for entry-level candidates "
    "(college students and fresh graduates). Ask exactly ONE clear interview "
    "question in simple, professional English for the given role. Ask only "
    "the question — no preamble, no greetings, no explanation, no follow-up. "
    "Keep it to a single sentence or two at most. Never repeat a question that "
    "the candidate has already been asked; if a list of previous questions is "
    "provided, ask about a different topic."
)


def build_agent() -> Agent:
    """Create the interviewer agent backed by the configured model.

    ``callback_handler=None`` disables Strands' default console output so the
    caller controls exactly what is printed and when.
    """
    return Agent(model=get_model(), system_prompt=SYSTEM_PROMPT, callback_handler=None)


def ask_question(
    role: str,
    asked: Sequence[str] | None = None,
    agent: Agent | None = None,
) -> str:
    """Ask one English interview question for ``role``.

    Args:
        role: Role identifier (e.g. "software", "data_analyst").
        asked: Questions already asked this session; the interviewer is told
            not to repeat them.
        agent: Optional pre-built agent (useful for tests); created if omitted.

    Returns:
        The interview question text.
    """
    agent = agent or build_agent()
    prompt = f"Ask one interview question for this role: {role_label(role)}."
    if asked:
        previous = "\n".join(f"- {q}" for q in asked)
        prompt += (
            "\n\nDo NOT repeat any of these already-asked questions; choose a "
            f"different topic:\n{previous}"
        )
    return str(agent(prompt)).strip()
