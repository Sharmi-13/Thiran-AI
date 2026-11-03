"""Interviewer agent.

A genuine ``strands.Agent`` that asks one English interview question for a
chosen role. To keep responses fast and free, the question comes from a local
question bank served by a Strands tool, so no Gemini call is made: the tool is
invoked directly via ``agent.tool.next_question`` (which does not go through
the model).
"""

from __future__ import annotations

from strands import Agent, tool

from ai import get_model

from ._common import role_label
from .question_bank import pick_question

SYSTEM_PROMPT = (
    "You are a professional job interviewer for entry-level candidates "
    "(college students and fresh graduates). You ask one clear interview "
    "question at a time using the next_question tool, never repeating a "
    "question the candidate has already been asked."
)


@tool
def next_question(role: str, asked: list[str] | None = None) -> str:
    """Return the next unused interview question for a role.

    Args:
        role: Role identifier (e.g. "software", "data_analyst").
        asked: Questions already asked this session, to avoid repeats.

    Returns:
        A single interview question string from the local question bank.
    """
    return pick_question(role, asked or [])


def build_agent() -> Agent:
    """Create the interviewer agent backed by the configured model.

    The agent is a real ``strands.Agent`` with the ``next_question`` tool.
    ``callback_handler=None`` disables Strands' default console output.
    """
    return Agent(
        model=get_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=[next_question],
        callback_handler=None,
    )


def _extract_text(tool_result: object) -> str:
    """Pull the question text out of a Strands tool-result dict."""
    if isinstance(tool_result, dict):
        for block in tool_result.get("content", []):
            if isinstance(block, dict) and "text" in block:
                return str(block["text"]).strip()
    return str(tool_result).strip()


def ask_question(
    role: str,
    asked: list[str] | None = None,
    agent: Agent | None = None,
) -> str:
    """Ask one English interview question for ``role`` with no Gemini call.

    The question is produced by calling the agent's ``next_question`` tool
    directly (``agent.tool.next_question``), which selects from the local
    question bank without invoking the model.

    Args:
        role: Role identifier (e.g. "software", "data_analyst").
        asked: Questions already asked this session; avoided when selecting.
        agent: Optional pre-built agent (useful for tests); created if omitted.

    Returns:
        The interview question text.
    """
    agent = agent or build_agent()
    # role_label validates/normalizes the role for display; the tool keys off
    # the raw identifier, so pass the identifier through to the bank.
    _ = role_label(role)
    result = agent.tool.next_question(role=role, asked=list(asked or []))
    return _extract_text(result)
