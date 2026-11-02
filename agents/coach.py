"""Coach agent.

A genuine ``strands.Agent`` that gives encouraging feedback in simple Tamil
plus an improved English sample answer. If the candidate answered in Tamil or
a mixed language, it also shows how to say the answer in interview English.
"""

from __future__ import annotations

from strands import Agent

from ai import get_model

SYSTEM_PROMPT = (
    "You are a supportive interview coach for college students and fresh "
    "graduates. Given an interview question and the candidate's answer, reply "
    "in this structure:\n"
    "1. Feedback in simple, encouraging Tamil (easy words a beginner "
    "understands). Point out what was good and what to improve. Give feedback "
    "on structure, detail and results. Do not criticise modest wording such "
    "as 'small' or 'simple'. Keep the Tamil feedback to 3 to 5 short, simple "
    "lines.\n"
    "2. An improved sample answer in clear, professional interview English, "
    "under the heading 'Improved English answer'.\n"
    "If the candidate answered in Tamil or in a mix of Tamil and English, also "
    "show, under the heading 'How to say it in interview English', how to "
    "express their answer in natural interview English.\n"
    "Keep it concise and practical."
)


def build_agent() -> Agent:
    """Create the coach agent backed by the configured model.

    ``callback_handler=None`` disables Strands' default console output so the
    caller controls what is printed and the text is not echoed twice.
    """
    return Agent(model=get_model(), system_prompt=SYSTEM_PROMPT, callback_handler=None)


def coach(question: str, answer: str, agent: Agent | None = None) -> str:
    """Return Tamil feedback plus an improved English sample answer.

    Args:
        question: The interview question that was asked.
        answer: The candidate's answer (text, any language).
        agent: Optional pre-built agent (useful for tests); created if omitted.

    Returns:
        The coaching text.
    """
    agent = agent or build_agent()
    prompt = (
        f"Interview question:\n{question}\n\n"
        f"Candidate's answer:\n{answer}\n\n"
        "Give your coaching feedback."
    )
    return str(agent(prompt)).strip()
