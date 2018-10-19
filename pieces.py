#!/usr/bin/env python3

"""pieces.py

Classes representing standard pieces of the Clue board game set.
"""

__author__ = 'Curtis Belmonte'

from enum import IntEnum
from typing import Sequence

import prefix


class Card(IntEnum):
    """Game card that either is held by a player or is part of the solution."""
    MUSTARD = 0
    PLUM = 1
    GREEN = 2
    PEACOCK = 3
    SCARLETT = 4
    WHITE = 5
    KNIFE = 6
    CANDLESTICK = 7
    REVOLVER = 8
    PIPE = 9
    ROPE = 10
    WRENCH = 11
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
    def parse(cls, card_prefix: str) -> 'Card':
        """Finds a card whose name matches the given prefix."""
        for name, card in cls.__members__.items():
            if prefix.is_match(card_prefix, name):
                return card
        raise KeyError('No card with prefix: ' + card_prefix)


# Cards representing murder suspects
SUSPECTS: Sequence[Card] = (
    Card.MUSTARD,
    Card.PLUM,
    Card.GREEN,
    Card.PEACOCK,
    Card.SCARLETT,
    Card.WHITE,
)

# Cards representing possible murder weapons
WEAPONS: Sequence[Card] = (
    Card.KNIFE,
    Card.CANDLESTICK,
    Card.REVOLVER,
    Card.PIPE,
    Card.ROPE,
    Card.WRENCH,
)

# Cards representing possible murder locations
ROOMS: Sequence[Card] = (
    Card.HALL,
    Card.LOUNGE,
    Card.DINING,
    Card.KITCHEN,
    Card.BALLROOM,
    Card.CONSERVATORY,
    Card.BILLIARD,
    Card.LIBRARY,
    Card.STUDY,
)
