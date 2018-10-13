#!/usr/bin/env python3

"""util.py

Collection of utility functions used by various other modules.
"""

__author__ = 'Curtis Belmonte'


def is_prefix_match(prefix: str, value: str) -> bool:
    """Checks if value has the given case-insensitive prefix."""
    return value.lower().startswith(prefix.lower())
