"""Shared, user-safe error messages.

Maps exceptions to short messages that are safe to show a student. The API
key and full exception text are never included in the returned message.
"""

from __future__ import annotations


def friendly_error(error: Exception) -> str:
    """Return one short, safe message for ``error``.

    Specific cases are detected from the exception text (status codes and
    common keywords). For anything unrecognized, only the exception's class
    name is shown — never the message body, which could contain sensitive
    details.
    """
    text = str(error).lower()

    # Order matters: check the more specific signals first.
    if "429" in text or "quota" in text or "rate limit" in text or "resource_exhausted" in text:
        return "Free usage limit reached. Please wait a minute and try again."
    if "404" in text or "not found" in text:
        return "Model name not found. Check GEMINI_MODEL in your .env file."
    if "401" in text or "403" in text or "unauthenticated" in text or "permission" in text or "api key" in text:
        return "API key was rejected. Check your GEMINI_API_KEY."
    if "timeout" in text or "timed out" in text or "deadline" in text:
        return "Timeout: Google did not respond. Please try again."
    if "503" in text or "unavailable" in text or "overloaded" in text:
        return "Google is busy right now. Please try again in a moment."

    # Fallback: reveal only the exception class name, nothing else.
    return f"Something went wrong ({type(error).__name__}). Please try again."
