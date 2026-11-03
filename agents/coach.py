"""Reviewer agent (merged evaluator + coach).

A single genuine ``strands.Agent`` that both scores the answer and produces
coaching feedback in one structured-output call, halving the number of model
calls per practice round (interviewer stays a separate call).

The call returns a :class:`Review` with scores plus two feedback fields:
``tamil_advice`` and ``improved_english``.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from strands import Agent

from ai import get_model


class Review(BaseModel):
    """Merged evaluation + coaching result for one answer.

    All scores are on a 0-10 scale.
    """

    content: int = Field(ge=0, le=10, description="Relevance and correctness of the answer, 0-10.")
    structure: int = Field(ge=0, le=10, description="Clarity and logical organization, 0-10.")
    english: int = Field(ge=0, le=10, description="Quality of professional English, 0-10.")
    overall: int = Field(ge=0, le=10, description="Overall score, 0-10.")
    notes: str = Field(description="One or two sentences summarizing the key feedback (internal; not shown).")
    tamil_advice: str = Field(
        description="3-5 short, friendly spoken-Tamil tips on how to improve "
        "THIS answer. Technical terms kept in English. Mention at least one "
        "thing the student actually said."
    )
    improved_english: str = Field(
        description="The student's own answer rewritten as a natural, "
        "moderate-level spoken interview English answer. English only, never "
        "Tamil. Keep the student's ideas; do not invent tools, numbers or "
        "projects; use placeholders like [your tool] or [X%] where details "
        "are missing."
    )


SYSTEM_PROMPT = (
    "You are a supportive interview reviewer for college students and fresh "
    "graduates. You BOTH score the candidate's answer AND coach them, in a "
    "single structured response. Given the interview question and the "
    "candidate's answer, produce these fields:\n"
    "- content, structure, english, overall: integer scores from 0 to 10.\n"
    "- notes: one or two sentences summarizing the key feedback.\n"
    "- tamil_advice: 3 to 5 short, friendly, spoken-style Tamil tips on how to "
    "improve THIS answer. Use easy everyday words, keep technical terms in "
    "English (for example: cache, API, database), keep each line short, and "
    "stay encouraging. Mention at least one specific thing the student "
    "actually said. Do not criticise modest wording such as 'small' or "
    "'simple'.\n"
    "- improved_english: rewrite what the student said as a proper, natural, "
    "moderate-level spoken interview English answer, whatever language they "
    "used (English, Tamil or Tanglish). Keep their own ideas. ALWAYS in "
    "English only, never in Tamil, because interviews are conducted in "
    "English. Follow STAR (Situation, Task, Action, Result) only where the "
    "student's own ideas allow, and never add details they did not say. Do "
    "NOT invent tools, numbers, companies, or projects; where a specific "
    "detail is missing, use a placeholder such as [your tool] or [X%] so the "
    "student fills it in.\n"
    "General rule: base every field on the question and the student's actual "
    "answer. In both notes and tamil_advice, mention at least one specific "
    "thing the student actually said (for example a tool, an action or a "
    "result they named). Never give generic advice that could apply to any "
    "answer.\n"
    "Scores must reflect this specific answer. Do not default to 7. Use the "
    "full 0-10 range: a very short or vague answer should score 3-5, a clear, "
    "specific, well-structured answer 7-9."
)


def build_agent() -> Agent:
    """Create the reviewer agent backed by the configured model.

    ``callback_handler=None`` disables Strands' default console output so the
    caller controls what is printed.
    """
    return Agent(model=get_model(), system_prompt=SYSTEM_PROMPT, callback_handler=None)


def review(question: str, answer: str, agent: Agent | None = None) -> Review:
    """Score and coach ``answer`` to ``question`` in one structured call.

    Args:
        question: The interview question that was asked.
        answer: The candidate's answer (text, any language).
        agent: Optional pre-built agent (useful for tests); created if omitted.

    Returns:
        A validated :class:`Review`.
    """
    agent = agent or build_agent()
    prompt = (
        f"Interview question:\n{question}\n\n"
        f"Candidate's answer:\n{answer}\n\n"
        "Score the answer and give your coaching feedback."
    )
    result = agent(prompt, structured_output_model=Review)
    return result.structured_output
