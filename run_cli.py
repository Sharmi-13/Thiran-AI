"""Terminal harness for Thiran AI.

Runs one full practice loop in the terminal:

    student id -> role -> interview question -> your answer ->
    evaluation scores (logged to results/attempts.csv) ->
    Tamil coaching feedback with an improved English sample answer.

Uses the configured AI provider via ``ai.factory.get_model`` (Gemini when
``AI_PROVIDER=gemini``). Run it yourself:

    .\\.venv\\Scripts\\python.exe run_cli.py

No API keys are printed by this script.
"""

from __future__ import annotations

from agents._common import ROLE_LABELS, DEFAULT_ROLE
from agents.coach import coach
from agents.evaluator import evaluate
from agents.interviewer import ask_question
from utils.attempts import record_attempt
from utils.errors import friendly_error


def _choose_role() -> str:
    """Prompt the user to pick a role, returning its identifier."""
    keys = list(ROLE_LABELS.keys())
    print("Choose a role:")
    for i, key in enumerate(keys, start=1):
        print(f"  {i}. {ROLE_LABELS[key]}")
    raw = input(f"Enter number (1-{len(keys)}) [default 1]: ").strip()
    if not raw:
        return DEFAULT_ROLE
    try:
        idx = int(raw)
        if 1 <= idx <= len(keys):
            return keys[idx - 1]
    except ValueError:
        pass
    print("Unrecognized choice, using the default role.")
    return DEFAULT_ROLE


def main() -> None:
    print("=== Thiran AI — terminal practice ===\n")

    student_id = input("Enter your student ID (short code like S01, no real name): ").strip()
    if not student_id:
        student_id = "S00"
        print("No ID given, using S00.")

    role = _choose_role()
    print(f"\nRole: {ROLE_LABELS[role]}\n")

    print("Interviewer is thinking...")
    try:
        question = ask_question(role)
    except Exception as error:  # noqa: BLE001 - surface a friendly message only
        print(friendly_error(error))
        return
    print(f"\nQuestion:\n{question}\n")

    answer = input("Your answer (type in English, Tamil, or mixed):\n> ").strip()
    if not answer:
        print("\nNo answer given. Exiting.")
        return

    print("\nEvaluator is scoring your answer...")
    try:
        evaluation = evaluate(question, answer)
    except Exception as error:  # noqa: BLE001
        print(friendly_error(error))
        return

    print("\n--- Scores (out of 10) ---")
    print(f"  Content   : {evaluation.content}")
    print(f"  Structure : {evaluation.structure}")
    print(f"  English   : {evaluation.english}")
    print(f"  Overall   : {evaluation.overall}")
    print(f"  Notes     : {evaluation.notes}")

    attempt_number = record_attempt(
        student_id=student_id,
        role=role,
        content=evaluation.content,
        structure=evaluation.structure,
        english=evaluation.english,
        overall=evaluation.overall,
    )
    print(f"\n(Logged attempt #{attempt_number} for {student_id} to results/attempts.csv)")

    print("\nCoach is preparing feedback...")
    try:
        feedback = coach(question, answer)
    except Exception as error:  # noqa: BLE001
        print(friendly_error(error))
        return

    print("\n--- Coaching feedback ---")
    print(feedback)


if __name__ == "__main__":
    main()
