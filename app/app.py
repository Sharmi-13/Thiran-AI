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
        "review": None,
        "answer": "",
        "error": None,
        "asked_questions": [],  # no-repeat history for the interviewer
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _reset_for_next_question() -> None:
    """Clear the current answer and results, keeping the asked history."""
    st.session_state.question = None
    st.session_state.answer = ""
    st.session_state.review = None
    st.session_state.error = None


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


# --- rendering helpers -------------------------------------------------------

def _score_colour(score: int) -> str:
    """Return a background colour for a 0-10 score band."""
    if score >= 7:
        return "#2e7d32"  # green
    if score >= 4:
        return "#f9a825"  # amber
    return "#c62828"  # red


def _score_card(label_en: str, label_ta: str, score: int) -> str:
    """Return HTML for a single colour-coded score card."""
    colour = _score_colour(score)
    return (
        f"<div style='background:{colour};color:white;border-radius:10px;"
        f"padding:12px 8px;text-align:center;'>"
        f"<div style='font-size:0.8rem;opacity:0.9;'>{label_en}<br>{label_ta}</div>"
        f"<div style='font-size:1.8rem;font-weight:700;'>{score}</div>"
        f"<div style='font-size:0.75rem;opacity:0.85;'>/ 10</div>"
        f"</div>"
    )


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
            "Role / பங்கு",
            options=role_keys,
            index=role_keys.index(DEFAULT_ROLE),
            format_func=lambda key: ROLE_LABELS[key],
        )

    st.info("Tip: Use STAR — Situation, Task, Action, Result.")

    # ---- Step 1: Get question -------------------------------------------
    st.header("1. Get question / கேள்வி பெறுங்கள்")
    if st.button("Get question / கேள்வி பெறுங்கள்"):
        st.session_state.error = None
        try:
            from agents.interviewer import ask_question

            question = ask_question(role, asked=st.session_state.asked_questions)
            st.session_state.question = question
            if question and question not in st.session_state.asked_questions:
                st.session_state.asked_questions.append(question)
            # Clear any previous results for the new question.
            st.session_state.review = None
            st.session_state.answer = ""
        except Exception as error:  # noqa: BLE001 - show a friendly message only
            st.session_state.error = friendly_error(error)
            st.session_state.question = None

    if st.session_state.error:
        st.error(st.session_state.error)

    if st.session_state.question:
        st.success(st.session_state.question)

    # ---- Step 2: Your answer --------------------------------------------
    st.header("2. Your answer / உங்கள் பதில்")
    if st.session_state.question:
        st.session_state.answer = st.text_area(
            "Type in English, Tamil, or mixed / ஆங்கிலம், தமிழ் அல்லது கலந்து",
            value=st.session_state.answer,
            height=160,
        )

        can_submit = bool(student_id) and bool(st.session_state.answer.strip())
        if not student_id:
            st.info("Enter a student ID in the sidebar to submit. / பக்கப்பட்டியில் மாணவர் ID-ஐ உள்ளிடவும்.")

        if st.button("Submit answer / பதிலை சமர்ப்பிக்கவும்", disabled=not can_submit):
            st.session_state.error = None
            question = st.session_state.question
            answer = st.session_state.answer.strip()
            with st.spinner("Thinking... / யோசிக்கிறது..."):
                try:
                    # One merged structured call (evaluator + coach combined).
                    from agents.coach import review

                    result = review(question, answer)

                    # Log scores only (no answer text, no personal data).
                    record_attempt(
                        student_id=student_id,
                        role=role,
                        content=result.content,
                        structure=result.structure,
                        english=result.english,
                        overall=result.overall,
                    )
                    st.session_state.review = result
                except Exception as error:  # noqa: BLE001
                    st.session_state.error = friendly_error(error)
                    st.session_state.review = None

            if st.session_state.error:
                st.error(st.session_state.error)
    else:
        st.caption("Get a question first. / முதலில் ஒரு கேள்வியைப் பெறுங்கள்.")

    # ---- Step 3: Feedback -----------------------------------------------
    st.header("3. Feedback / கருத்து")
    review = st.session_state.review
    if review is not None:
        st.subheader("Scores / மதிப்பெண்கள் (out of 10)")
        cols = st.columns(4)
        cards = [
            ("Content", "உள்ளடக்கம்", review.content),
            ("Structure", "அமைப்பு", review.structure),
            ("English", "ஆங்கிலம்", review.english),
            ("Overall", "மொத்தம்", review.overall),
        ]
        for col, (en, ta, score) in zip(cols, cards):
            col.markdown(_score_card(en, ta, score), unsafe_allow_html=True)

        # Exactly two feedback boxes, straight from the structured fields.
        # (notes is kept in the model but intentionally not shown.)
        tamil_advice = (review.tamil_advice or "").strip()
        improved_english = (review.improved_english or "").strip()

        if tamil_advice:
            st.markdown("**தமிழ் அறிவுரை / Tamil tips**")
            with st.container(border=True):
                st.markdown(tamil_advice)

        if improved_english:
            st.markdown("**Interview English / நேர்காணல் ஆங்கிலம்**")
            with st.container(border=True):
                st.markdown(improved_english)

        if st.button("Next question / அடுத்த கேள்வி"):
            _reset_for_next_question()
            st.rerun()

    # ---- Progress --------------------------------------------------------
    if student_id:
        st.header("My progress / என் முன்னேற்றம்")
        rows = _progress_rows(student_id)
        if rows:
            attempts = [a for a, _ in rows]
            overalls = [o for _, o in rows]
            # Whole-number attempt numbers on the x-axis.
            chart_data = {"attempt_number": attempts, "overall": overalls}
            st.line_chart(chart_data, x="attempt_number", y="overall")
            st.caption(
                f"Your overall score: first attempt {overalls[0]} to latest {overalls[-1]}."
            )
        else:
            st.info("No attempts yet for this student ID. / இன்னும் முயற்சிகள் இல்லை.")


main()
