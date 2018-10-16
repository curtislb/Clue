#!/usr/bin/env python3

"""trackers.py

Convenience classes for keeping track of the current state of the game.
"""

__author__ = 'Curtis Belmonte'

from collections import defaultdict
from operator import itemgetter
from typing import DefaultDict, Dict, List, Set, Tuple

import util
from pieces import Card


class ShownCardTracker(object):
    """Keeps track of the cards that the user has shown to other players."""

    def __init__(self, opponents: List[str], own_cards: List[Card]) -> None:
        self._opponents = opponents
        self._shown_players: Dict[Card, Set[str]] = {
            card: set() for card in own_cards
        }

    def __repr__(self) -> str:
        lines = ['Shown Cards:']

        # Show the list of players who have seen each card
        for card, players in sorted(
            self._shown_players.items(),
            key=itemgetter(0)
        ):
            if players:
                lines.append('{}: {}'.format(
                    card.name,
                    ', '.join(sorted(players))
                ))

        return '\n'.join(lines)

    def update(self, opponent: str, card: Card) -> None:
        """Updates tracker after an opponent has been shown the given card."""
        self._shown_players[card].add(self._find_opponent(opponent))

    def _find_opponent(self, opponent_prefix: str) -> str:
        """Finds the full name of an opponent matching the given prefix."""
        opponent = util.find_prefix_match(opponent_prefix, self._opponents)
        if opponent is None:
            raise ValueError('No opponent with prefix: ' + opponent_prefix)
        return opponent


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
        showing_player: str
    ) -> None:
        """Updates player/card counts after a suggestion has been made."""
        player_name = self._find_player(player)
        for card in cards:
            count, showing_players = self._suggestions[player_name][card]
            showing_players.add(self._find_player(showing_player))
            self._suggestions[player_name][card] = (count + 1, showing_players)

    def _find_player(self, player_prefix: str) -> str:
        """Finds the full name of a player matching the given prefix."""
        player = util.find_prefix_match(player_prefix, self._suggestions.keys())
        if player is None:
            raise ValueError('No player with prefix: ' + player_prefix)
        return player
