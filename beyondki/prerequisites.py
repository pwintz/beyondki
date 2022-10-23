"""Functions for parsing Anki note prerequisites from tags."""
from typing import Optional, Iterable

PREFIX = "pre:"
DELIM = " "


def parse_prerequisite_tag(tag: str) -> Optional[str]:
    """
    Attempt to parse a prerequisite from a single raw tag.

    Return the prerequisite as a string if the tag is, in fact, a prerequisite.
    Otherwise, return ``None``.
    """
    if tag.startswith(PREFIX):
        return tag[len(PREFIX):]
    return None


def extract_prerequisite_tags(s: str) -> list[str]:
    """Parse prerequisite tags from a string."""
    # Strip leading and trailing whitespace, and split on the tag delimiter.
    tags: list[str] = s.strip().split(DELIM)

    # Try to parse each tag as a prerequisite.
    tags: Iterable[Optional[str]] = map(parse_prerequisite_tag, tags)

    # Filter out the ``None`` values, i.e. non-prereq tags.
    return list(filter(lambda t: t is not None, tags))
