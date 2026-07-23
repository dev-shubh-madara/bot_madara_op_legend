"""
Shared utilities for message formatting.
"""
import html


def bq(text: str) -> str:
    """Wrap text in a Telegram HTML blockquote."""
    return f"<blockquote>{text}</blockquote>"


def esc(text: str) -> str:
    """HTML-escape dynamic user content (names, usernames, etc.)."""
    return html.escape(str(text))
