"""Terminal harness for Thiran AI.

Runs one full practice loop in the terminal:

    student id -> role -> interview question -> your answer ->
    one merged review call: scores (logged to results/attempts.csv) plus
    Tamil advice, an improved English sample answer, and how to say it.

Uses the configured AI provider via ``ai.factory.get_model`` (Gemini when
``AI_PROVIDER=gemini``). Run it yourself:

    .\\.venv\\Scripts\\python.exe run_cli.py

No API keys are printed by this script.
"""

from __future__ import annotations

from agents._common import ROLE_LABELS, DEFAULT_ROLE
from agents.coach import review
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

    print("\nReviewing your answer...")
    try:
        result = review(question, answer)
    except Exception as error:  # noqa: BLE001
        print(friendly_error(error))
        return

    print("\n--- Scores (out of 10) ---")
    print(f"  Content   : {result.content}")
    print(f"  Structure : {result.structure}")
    print(f"  English   : {result.english}")
    print(f"  Overall   : {result.overall}")

    attempt_number = record_attempt(
        student_id=student_id,
        role=role,
        content=result.content,
        structure=result.structure,
        english=result.english,
        overall=result.overall,
    )
    print(f"\n(Logged attempt #{attempt_number} for {student_id} to results/attempts.csv)")

    print("\n--- தமிழ் அறிவுரை / Tamil tips ---")
    print(result.tamil_advice)

    print("\n--- Interview English / நேர்காணல் ஆங்கிலம் ---")
    print(result.improved_english)


if __name__ == "__main__":
    main()
