"""Score-trend logging for practice attempts.

Appends one row per evaluation to ``results/attempts.csv`` so a student's
score trend can be reviewed over time. Only scores and non-personal metadata
are stored: never the answer text, and the student is identified by a short
self-chosen code (e.g. "S01"), not a real name.

Columns:
    student_id, attempt_number, timestamp, role, content, structure,
    english, overall
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

RESULTS_DIR = Path("results")
ATTEMPTS_CSV = RESULTS_DIR / "attempts.csv"

FIELDNAMES = [
    "student_id",
    "attempt_number",
    "timestamp",
    "role",
    "content",
    "structure",
    "english",
    "overall",
]


def _ensure_file() -> None:
    """Create the results directory and header row if they do not exist."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not ATTEMPTS_CSV.exists():
        with ATTEMPTS_CSV.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(FIELDNAMES)


def count_attempts(student_id: str) -> int:
    """Return how many rows already exist for ``student_id``."""
    if not ATTEMPTS_CSV.exists():
        return 0
    student_id = student_id.strip()
    count = 0
    with ATTEMPTS_CSV.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if (row.get("student_id") or "").strip() == student_id:
                count += 1
    return count


def record_attempt(
    student_id: str,
    role: str,
    content: int,
    structure: int,
    english: int,
    overall: int,
) -> int:
    """Append one attempt row and return its attempt number.

    The attempt number is derived by counting the student's existing rows, so
    it is stable even across separate runs.

    Args:
        student_id: Short student code (e.g. "S01"); no real names.
        role: Role identifier for the practice session.
        content: Content score (0-10).
        structure: Structure score (0-10).
        english: English score (0-10).
        overall: Overall score (0-10).

    Returns:
        The 1-based attempt number assigned to this row.
    """
    _ensure_file()
    student_id = student_id.strip()
    attempt_number = count_attempts(student_id) + 1
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with ATTEMPTS_CSV.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                student_id,
                attempt_number,
                timestamp,
                role,
                content,
                structure,
                english,
                overall,
            ]
        )
    return attempt_number
