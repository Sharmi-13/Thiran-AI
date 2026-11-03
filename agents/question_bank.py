"""Pre-written interview question bank.

Ten realistic English questions per role, mixing common fresher questions
(e.g. "Tell me about yourself") with role-specific ones. The interviewer
picks from this bank locally, so no Gemini call is needed to ask a question.

Lookup: ``QUESTION_BANK[role]`` -> list[str].
"""

from __future__ import annotations

from collections.abc import Sequence

QUESTION_BANK: dict[str, list[str]] = {
    "software": [
        "Tell me about yourself.",
        "Why should we hire you?",
        "Why do you want to work as a software developer?",
        "Can you explain the difference between a list and a tuple, and when you would use each?",
        "Walk me through how you would debug a program that crashes only sometimes.",
        "What is the difference between a stack and a queue, with an example of where each is used?",
        "How do you make sure your code is readable and easy for others to maintain?",
        "Tell me about a project you built and what your specific contribution was.",
        "How would you explain what an API is to a non-technical person?",
        "What do you do when you get stuck on a problem you cannot solve?",
    ],
    "data_analyst": [
        "Tell me about yourself.",
        "Why should we hire you?",
        "Why are you interested in a data analyst role?",
        "What is the difference between a primary key and a foreign key in a database?",
        "How would you find the top 3 products by revenue in each region using SQL?",
        "How do you handle missing or inconsistent data before an analysis?",
        "How would you explain a trend in the data to a manager who is not technical?",
        "Tell me about a time you used data to answer a question or solve a problem.",
        "What is the difference between a bar chart and a histogram, and when would you use each?",
        "How do you check whether your analysis is accurate before sharing it?",
    ],
    "customer_support": [
        "Tell me about yourself.",
        "Why should we hire you?",
        "Why do you want to work in customer support?",
        "How would you respond to a customer who is frustrated about a delayed order?",
        "A customer asks for a refund that is outside policy. How do you handle it?",
        "How do you stay calm and patient when a customer is angry?",
        "How would you explain a technical issue in simple words to a customer?",
        "Tell me about a time you helped someone solve a difficult problem.",
        "How do you handle several customers needing help at the same time?",
        "What would you do if you did not know the answer to a customer's question?",
    ],
    "business_marketing": [
        "Tell me about yourself.",
        "Why should we hire you?",
        "Why do you want to work in business and marketing?",
        "How would you explain the difference between marketing and sales?",
        "How would you measure whether a social media campaign was successful?",
        "Walk me through how you would launch a new product with a limited budget.",
        "How would you describe our product to a customer who has never heard of it?",
        "Tell me about a time you persuaded someone to accept your idea.",
        "What makes a marketing message memorable, in your opinion?",
        "How would you decide which customer group to target first for a new product?",
    ],
}

DEFAULT_ROLE = "software"


def pick_question(role: str, asked: Sequence[str] | None = None) -> str:
    """Return the first bank question for ``role`` that is not in ``asked``.

    Args:
        role: Role identifier; unknown roles fall back to the default role.
        asked: Questions already asked this session.

    Returns:
        A question string. If every bank question has already been asked, the
        first question for the role is returned (cycles rather than failing).
    """
    questions = QUESTION_BANK.get(role, QUESTION_BANK[DEFAULT_ROLE])
    already = set(asked or ())
    for question in questions:
        if question not in already:
            return question
    return questions[0]
