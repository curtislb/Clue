#!/usr/bin/env python3

"""pieces.py

Classes representing standard pieces of the Clue board game set.
"""

from enum import IntEnum

import util


class Card(IntEnum):
    """Game card that either is held by a player or is part of the solution."""

    # Suspects
    MUSTARD = 0
    PLUM = 1
    GREEN = 2
    PEACOCK = 3
    SCARLETT = 4
    WHITE = 5

    # Weapons
    KNIFE = 6
    CANDLESTICK = 7
    REVOLVER = 8
    PIPE = 9
    ROPE = 10
    WRENCH = 11

    # Rooms
    HALL = 12
    LOUNGE = 13
    DINING = 14
    KITCHEN = 15
    BALLROOM = 16
    CONSERVATORY = 17
    BILLIARD = 18
    LIBRARY = 19
    STUDY = 20

    @classmethod
    def parse(cls, prefix: str) -> 'Card':
        """Finds a card whose name matches the given prefix."""
        for name, card in cls.__members__.items():
            if util.is_prefix_match(prefix, name):
                return card
        raise KeyError('No card with prefix: ' + prefix)
