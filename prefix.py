#!/usr/bin/env python3

"""prefix.py

Utility functions related to string prefix matching.
"""

__author__ = 'Curtis Belmonte'

from typing import Iterable


def find_match(prefix: str, values: Iterable[str]) -> str:
    """Finds and returns a value with the given case-insensitive prefix."""
    for value in values:
        if is_match(prefix, value):
            return value
    raise ValueError("No value with prefix '{}' in {}".format(prefix, values))


def is_match(prefix: str, value: str) -> bool:
    """Checks if value has the given case-insensitive prefix."""
    return value.lower().startswith(prefix.lower())
