"""Thiran AI — Streamlit page.

English mock interview with feedback in Tamil. The page loads without any API
key: the agents (and therefore the model) are only constructed after the user
clicks a button, never at import time.

Run with:

    streamlit run app/app.py

Testing without a key: set AI_PROVIDER=mock in the environment.
"""

from __future__ import annotations

import csv
from pathlib import Path

import streamlit as st

from agents._common import ROLE_LABELS, DEFAULT_ROLE
from utils.attempts import ATTEMPTS_CSV, record_attempt
from utils.errors import friendly_error


# --- session state -----------------------------------------------------------

def _init_state() -> None:
    """Initialize session keys so values persist across reruns/clicks."""
    defaults = {
        "question": None,
        "evaluation": None,
        "coaching": None,
        "answer": "",
        "error": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


# --- progress chart data (stdlib csv, no pandas) -----------------------------

def _progress_rows(student_id: str) -> list[tuple[int, int]]:
    """Return (attempt_number, overall) pairs for ``student_id``, ordered."""
    student_id = student_id.strip()
    if not student_id or not Path(ATTEMPTS_CSV).exists():
        return []
    rows: list[tuple[int, int]] = []
    with open(ATTEMPTS_CSV, "r", newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if (row.get("student_id") or "").strip() != student_id:
                continue
            try:
                rows.append((int(row["attempt_number"]), int(row["overall"])))
            except (KeyError, ValueError):
                continue
    rows.sort(key=lambda r: r[0])
    return rows


# --- page --------------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title="Thiran AI", page_icon="🎯")
    _init_state()

    st.title("Thiran AI")
    st.caption("English mock interview, feedback in Tamil.")

    # Sidebar: student id + role.
    with st.sidebar:
        st.header("Session")
        student_id = st.text_input("Student ID", placeholder="S01").strip()
        st.caption("Use a short code like S01. Do not enter real names.")
        role_keys = list(ROLE_LABELS.keys())
        role = st.selectbox(
            "Role",
            options=role_keys,
            index=role_keys.index(DEFAULT_ROLE),
            format_func=lambda key: ROLE_LABELS[key],
        )

    # Get question: constructs the interviewer agent only on click.
    if st.button("Get question"):
        st.session_state.error = None
        try:
            from agents.interviewer import ask_question

            st.session_state.question = ask_question(role)
            # Clear any previous results for the new question.
            st.session_state.evaluation = None
            st.session_state.coaching = None
            st.session_state.answer = ""
        except Exception as error:  # noqa: BLE001 - show a friendly message only
            st.session_state.error = friendly_error(error)
            st.session_state.question = None

    if st.session_state.error:
        st.error(st.session_state.error)

    # Question + answer flow.
    if st.session_state.question:
        st.subheader("Question")
        st.write(st.session_state.question)

        st.session_state.answer = st.text_area(
            "Your answer (English, Tamil, or mixed)",
            value=st.session_state.answer,
            height=160,
        )

        can_submit = bool(student_id) and bool(st.session_state.answer.strip())
        if not student_id:
            st.info("Enter a student ID in the sidebar to submit.")

        if st.button("Submit answer", disabled=not can_submit):
            st.session_state.error = None
            question = st.session_state.question
            answer = st.session_state.answer.strip()
            with st.spinner("Thinking..."):
                try:
                    from agents.evaluator import evaluate
                    from agents.coach import coach

                    evaluation = evaluate(question, answer)
                    coaching = coach(question, answer)

                    # Log scores only (no answer text, no personal data).
                    record_attempt(
                        student_id=student_id,
                        role=role,
                        content=evaluation.content,
                        structure=evaluation.structure,
                        english=evaluation.english,
                        overall=evaluation.overall,
                    )
                    st.session_state.evaluation = evaluation
                    st.session_state.coaching = coaching
                except Exception as error:  # noqa: BLE001
                    st.session_state.error = friendly_error(error)
                    st.session_state.evaluation = None
                    st.session_state.coaching = None

            if st.session_state.error:
                st.error(st.session_state.error)

    # Results.
    evaluation = st.session_state.evaluation
    if evaluation is not None:
        st.subheader("Scores (out of 10)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Content", evaluation.content)
        c2.metric("Structure", evaluation.structure)
        c3.metric("English", evaluation.english)
        c4.metric("Overall", evaluation.overall)
        st.write(evaluation.notes)

    if st.session_state.coaching:
        st.subheader("Coaching feedback")
        st.markdown(st.session_state.coaching)

    # My progress.
    if student_id:
        st.subheader("My progress")
        rows = _progress_rows(student_id)
        if rows:
            # Index "overall" by attempt_number so the x-axis is the attempt.
            chart_data = {
                "attempt_number": [attempt for attempt, _ in rows],
                "overall": [overall for _, overall in rows],
            }
            st.line_chart(chart_data, x="attempt_number", y="overall")
            st.caption(
                "Overall score by attempt number for "
                f"{student_id} ({len(rows)} attempt(s))."
            )
        else:
            st.info("No attempts yet for this student ID.")


main()
