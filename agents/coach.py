"""Reviewer agent (merged evaluator + coach).

A single genuine ``strands.Agent`` that both scores the answer and produces
coaching feedback in one structured-output call, halving the number of model
calls per practice round (interviewer stays a separate call).

The call returns a :class:`Review` with scores plus three feedback fields:
``tamil_advice``, ``improved_english`` and ``how_to_say_it``.
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
    notes: str = Field(description="One or two sentences summarizing the key feedback.")
    tamil_advice: str = Field(
        description="3-5 short, friendly spoken-Tamil lines of advice on how to "
        "improve the answer (structure, detail, results). Technical terms kept "
        "in English. Never criticise modest wording."
    )
    improved_english: str = Field(
        description="A sample answer in English only (never Tamil), in natural "
        "spoken interview English using STAR, faithful to what the student said, "
        "with placeholders like [your tool] and [X%] instead of invented details."
    )
    how_to_say_it: str = Field(
        description="If the student answered in Tamil or Tanglish: 2-3 key "
        "phrases from their own answer converted to interview English. If the "
        "student answered in English: 2-3 phrases to improve as 'Instead of X, "
        "say Y'."
    )


SYSTEM_PROMPT = (
    "You are a supportive interview reviewer for college students and fresh "
    "graduates. You BOTH score the candidate's answer AND coach them, in a "
    "single structured response. Given the interview question and the "
    "candidate's answer, produce these fields:\n"
    "- content, structure, english, overall: integer scores from 0 to 10.\n"
    "- notes: one or two sentences summarizing the key feedback.\n"
    "- tamil_advice: 3 to 5 short, friendly, spoken-style Tamil lines advising "
    "how to improve the answer (structure, detail, results). Use easy everyday "
    "words, keep technical terms in English (for example: cache, API, "
    "database), keep each line short, and stay encouraging. Do not criticise "
    "modest wording such as 'small' or 'simple'.\n"
    "- improved_english: a sample answer ALWAYS in English only, never in "
    "Tamil, in natural spoken interview English using STAR (Situation, Task, "
    "Action, Result). Interviews are conducted in English, so never give the "
    "sample answer in Tamil. Keep it faithful to what the student actually "
    "said: do NOT invent tools, numbers, companies, or projects. Where a "
    "specific detail is missing, use a placeholder such as [your tool] or "
    "[X%] so the student fills it in.\n"
    "- how_to_say_it: if the student answered in Tamil or in a mix of Tamil "
    "and English (Tanglish), give 2 or 3 key phrases from their own answer "
    "converted to interview English. If the student answered in English, give "
    "2 or 3 phrases they could say better, each as 'Instead of X, say Y'.\n"
    "General rule: base every field on the question and the student's actual "
    "answer. In both notes and tamil_advice, mention at least one specific "
    "thing the student actually said (for example a tool, an action or a "
    "result they named). Never give generic advice that could apply to any "
    "answer."
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
