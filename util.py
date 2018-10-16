#!/usr/bin/env python3

"""util.py

Collection of utility functions used by various other modules.
"""

__author__ = 'Curtis Belmonte'

from typing import Iterable, Optional


def find_prefix_match(prefix: str, values: Iterable[str]) -> Optional[str]:
    """Tries to find a value matching the given case-insensitive prefix."""
    for value in values:
        if is_prefix_match(prefix, value):
            return value
    return None


def is_prefix_match(prefix: str, value: str) -> bool:
    """Checks if value has the given case-insensitive prefix."""
    return value.lower().startswith(prefix.lower())
