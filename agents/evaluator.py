"""Evaluator agent.

A genuine ``strands.Agent`` that scores a candidate's answer using Strands
structured output. Scores content, structure, and English each out of 10,
plus an overall score and short notes.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from strands import Agent

from ai import get_model


class Evaluation(BaseModel):
    """Structured evaluation of a candidate's answer.

    All scores are on a 0-10 scale.
    """

    content: int = Field(ge=0, le=10, description="Relevance and correctness of the answer, 0-10.")
    structure: int = Field(ge=0, le=10, description="Clarity and logical organization, 0-10.")
    english: int = Field(ge=0, le=10, description="Quality of professional English, 0-10.")
    overall: int = Field(ge=0, le=10, description="Overall score, 0-10.")
    notes: str = Field(description="One or two sentences summarizing the key feedback.")


SYSTEM_PROMPT = (
    "You are a strict but fair interview evaluator for entry-level candidates. "
    "Given an interview question and the candidate's answer, score the answer "
    "on three dimensions, each from 0 to 10: content (relevance and "
    "correctness), structure (clarity and logical flow), and english (quality "
    "of professional English). Also give an overall score from 0 to 10 and a "
    "short note summarizing the most important feedback. Be objective and "
    "consistent."
)


def build_agent() -> Agent:
    """Create the evaluator agent backed by the configured model.

    ``callback_handler=None`` disables Strands' default console output
    (including tool-use lines) so the caller controls what is printed.
    """
    return Agent(model=get_model(), system_prompt=SYSTEM_PROMPT, callback_handler=None)


def evaluate(question: str, answer: str, agent: Agent | None = None) -> Evaluation:
    """Score ``answer`` to ``question`` and return a structured result.

    Args:
        question: The interview question that was asked.
        answer: The candidate's answer (text).
        agent: Optional pre-built agent (useful for tests); created if omitted.

    Returns:
        A validated :class:`Evaluation`.
    """
    agent = agent or build_agent()
    prompt = (
        f"Interview question:\n{question}\n\n"
        f"Candidate's answer:\n{answer}\n\n"
        "Evaluate the answer and provide the scores."
    )
    result = agent(prompt, structured_output_model=Evaluation)
    return result.structured_output
