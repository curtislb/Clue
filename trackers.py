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
                    ', '.join([card.name for card in sorted(cards)])
                ))

        return '\n'.join(lines)

    def update(self, opponent: str, card: Card) -> None:
        """Updates tracker after an opponent has been shown the given card."""
        self._shown_cards[opponent].add(card)


class SuggestionTracker(object):
    """Keeps track of suggestions that are made and disproved by players."""

    # Type aliases for suggestion data stored in tracker
    CardInfo = Tuple[int, Set[str]]
    PlayerInfo = DefaultDict[Card, CardInfo]

    def __init__(self, all_players: List[str]) -> None:
        self._suggestions: Dict[str, 'SuggestionTracker.PlayerInfo'] = {
            player: defaultdict(lambda: (0, set())) for player in all_players
        }

    def __repr__(self) -> str:
        lines = ['Suggestions:']

        # Show card counts for each player in descending order
        for player, info in self._suggestions.items():
            if info:
                lines.append('  {}:'.format(player))
                sorted_info: List[
                    Tuple[Card, 'SuggestionTracker.CardInfo']
                ] = sorted(
                    info.items(),
                    key=lambda item: (item[1][0], -item[0]),
                    reverse=True
                )
                for card, card_info in sorted_info:
                    count, showing_players = card_info
                    lines.append('    {:13s} {} ({})'.format(
                        card.name + ':',
                        count,
                        ', '.join(sorted(showing_players))
                    ))

        return '\n'.join(lines)

    def update(
        self,
        player: str,
        cards: List[Card],
        showing_player: Optional[str]
    ) -> None:
        """Updates player/card counts after a suggestion has been made."""
        for card in cards:
            count, showing_players = self._suggestions[player][card]
            if showing_player is not None:
                showing_players.add(showing_player)
            self._suggestions[player][card] = (count + 1, showing_players)
