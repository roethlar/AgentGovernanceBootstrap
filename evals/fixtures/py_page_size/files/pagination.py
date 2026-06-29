MAX_PAGE_SIZE = 100


def parse_page_size(raw):
    """Parse a user-supplied page-size parameter.

    Syntax: surrounding whitespace allowed; the value itself must be decimal
    digits; the parsed integer must be in [1, MAX_PAGE_SIZE].
    """
    if not isinstance(raw, str):
        raise TypeError("page size must be a string")
    if not raw.isdigit():            # bug: rejects valid " 25\n" (surrounding whitespace)
        raise ValueError("page size must contain only digits")
    value = int(raw)
    if value < 1 or value > MAX_PAGE_SIZE:
        raise ValueError("page size out of range")
    return value
