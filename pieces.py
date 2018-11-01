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

    GREEN = 0
    MUSTARD = 1
    ORCHID = 2
    PEACOCK = 3
    PLUM = 4
    SCARLETT = 5
    CANDLESTICK = 6
    DAGGER = 7
    PIPE = 8
    REVOLVER = 9
    ROPE = 10
    WRENCH = 11
    BALLROOM = 12
    BILLIARD = 13
    CONSERVATORY = 14
    DINING = 15
    HALL = 16
    KITCHEN = 17
    LIBRARY = 18
    LOUNGE = 19
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
    Card.GREEN,
    Card.MUSTARD,
    Card.ORCHID,
    Card.PEACOCK,
    Card.PLUM,
    Card.SCARLETT,
)

# Cards representing possible murder weapons
WEAPONS: Sequence[Card] = (
    Card.CANDLESTICK,
    Card.DAGGER,
    Card.PIPE,
    Card.REVOLVER,
    Card.ROPE,
    Card.WRENCH,
)

# Cards representing possible murder locations
ROOMS: Sequence[Card] = (
    Card.BALLROOM,
    Card.BILLIARD,
    Card.CONSERVATORY,
    Card.DINING,
    Card.HALL,
    Card.KITCHEN,
    Card.LIBRARY,
    Card.LOUNGE,
    Card.STUDY,
)
