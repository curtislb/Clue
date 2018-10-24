#!/usr/bin/env python3

"""trackers.py

Convenience classes for keeping track of the current state of the game.
"""

__author__ = 'Curtis Belmonte'

from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Set, Tuple

from pieces import Card


class ShownCardTracker(object):
    """Keeps track of the cards that the user has shown to other players."""

    def __init__(self, opponents: List[str]) -> None:
        self._shown_cards: Dict[str, Set[Card]] = {
            opponent: set() for opponent in opponents
        }

    def __repr__(self) -> str:
        lines = ['Shown Cards:']

        # Show the list of players who have seen each card
        for player, cards in self._shown_cards.items():
            if cards:
                lines.append('  {}: {}'.format(
                    player,
                    ', '.join(card.name for card in sorted(cards))
                ))

        return '\n'.join(lines)

    def update(self, opponent: str, card: Card) -> None:
        """Updates tracker after an opponent has been shown the given card."""
        self._shown_cards[opponent].add(card)


class SkippedCardTracker(object):
    """Keeps track of cards suggested by others that the user has skipped."""

    def __init__(self) -> None:
        self._skipped_cards: Set[Card] = set()

    def __repr__(self) -> str:
        lines = ['Skipped Cards:']
        if self._skipped_cards:
            lines.append(
                '  ' + ', '.join(c.name for c in sorted(self._skipped_cards))
            )
        return '\n'.join(lines)

    def update(self, cards: List[Card]) -> None:
        """Updates tracker after the player has skipped for the given cards."""
        for card in cards:
            self._skipped_cards.add(card)


class SuggestionTracker(object):
    """Keeps track of suggestions that are made and disproved by players."""

    # Type alias for suggestion data stored in tracker
    Info = Tuple[List[Card], List[str], Optional[str]]

    def __init__(self) -> None:
        self._suggestions: DefaultDict[
            str,
            List['SuggestionTracker.Info']
        ] = defaultdict(list)

    def __repr__(self) -> str:
        lines = ['Suggestions:']
        for player, suggestions in self._suggestions.items():
            lines.append('  {}:'.format(player))
            lines.extend([self._format_info(info) for info in suggestions])
        return '\n'.join(lines)

    def update(
        self,
        player: str,
        cards: List[Card],
        passing_players: List[str],
        showing_player: Optional[str]
    ) -> None:
        """Updates player/card counts after a suggestion has been made."""
        self._suggestions[player].append((
            cards,
            passing_players,
            showing_player,
        ))

    @staticmethod
    def _format_info(info: 'SuggestionTracker.Info') -> str:
        cards, passing_players, showing_player = info
        return '    {} -> [{}] -> {}'.format(
            ', '.join(card.name for card in cards),
            ', '.join(passing_players),
            showing_player
        )
