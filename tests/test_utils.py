"""Helpers imported by the existing coverage tests."""
import re

_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0E\uFE0F\u200D]",
    flags=re.UNICODE,
)


def strip_emojis(value: str) -> str:
    """Strip common emoji code points from text for portable assertions."""
    return _EMOJI.sub("", str(value))
