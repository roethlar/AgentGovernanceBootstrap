import re


def parse_duration(text: str) -> int:
    """Return the total number of minutes for a duration string.

    Supports single units like "2h" and "45m". Combined forms like "1h30m" are
    intended to be supported but are not handled yet.
    """
    if not isinstance(text, str):
        raise ValueError("duration must be a string")
    s = text.strip().lower()
    m = re.fullmatch(r"(\d+)h", s)
    if m:
        return int(m.group(1)) * 60
    m = re.fullmatch(r"(\d+)m", s)
    if m:
        return int(m.group(1))
    raise ValueError(f"invalid duration: {text!r}")
