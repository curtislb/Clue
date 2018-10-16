#!/usr/bin/env python3

"""ledger.py

Provides a ledger class for keeping notes and making deductions about the cards
that players hold and, by extension, the cards that make up the solution.
"""

__author__ = 'Curtis Belmonte'

from typing import Iterable, List, Optional, Set, Tuple

import util
from pieces import Card, ROOMS, SUSPECTS, WEAPONS


class Ledger(object):
    """Spreadsheet with information about players and their cards."""

    # Ledger entries with special meaning
    YES = {-1}  # player has card
    NO = {-2}   # player doesn't have card

    def __init__(
        self,
        all_players: List[str],
        player: str,
        own_cards: List[Card]
    ) -> None:
        self._all_players = all_players
        self._player = player
        self._hand_size = len(own_cards)
        self._sheet: List[List[Set[int]]] = [
            [set() for _ in all_players] for _ in Card.__members__
        ]

        # Update ledger based on player's held cards
        player_index = all_players.index(player)
        for card in sorted(Card.__members__.values()):
            if card in own_cards:
                self._sheet[card] = [
                    self.YES if i == player_index else self.NO
                    for i in range(len(all_players))
                ]
            else:
                self._sheet[card][player_index] = self.NO

    def __repr__(self) -> str:
        header = ' | '.join(
            [' ' * 14] + ['{:13s}'.format(name) for name in self._all_players]
        )
        divider = '-' * (15 + 16 * len(self._all_players))
        lines = ['', header, divider]

        # Add line for each game card, with an entry for each player
        for i, row in enumerate(self._sheet):
            row_label = '{:14s}'.format(Card(i).name)
            lines.append(' | '.join(
                [row_label] + [self._format_entry(entry) for entry in row]
            ))

        return '\n'.join(lines)

    def solve(self) -> Optional[Tuple[Card, Card, Card]]:
        """Returns the cards that make up the solution, or None if ambiguous."""
        suspects = self._find_possible_cards(SUSPECTS)
        weapons = self._find_possible_cards(WEAPONS)
        rooms = self._find_possible_cards(ROOMS)
        if len(suspects) == 1 and len(weapons) == 1 and len(rooms) == 1:
            solution = (suspects[0], weapons[0], rooms[0])
        else:
            solution = None
        return solution

    def update(
            self,
            cards: List[Card],
            passing_players: List[str],
            showing_player: str,
            shown_card: Optional[Card]
    ) -> None:
        """Updates the ledger after a suggestion has been made and disproved."""

        # Passing players can't have any of the given cards
        for player in passing_players:
            for card in cards:
                player_index = self._get_player_index(player)
                self._sheet[card][player_index] = self.NO

        # Update ledger based on showing player and/or shown card
        if shown_card is None:
            self._mark_other_shown(cards, showing_player)
        elif showing_player != self._player:
            self._mark_player_shown(shown_card, showing_player)

        # Make any deductions based on new info
        self._simplify()

    @classmethod
    def _format_entry(cls, entry: Set[int]) -> str:
        """Converts a ledger entry into a human-readable string."""
        if entry == cls.YES:
            entry_str = 'YES'
        elif entry == cls.NO:
            entry_str = 'NO'
        else:
            entry_str = ' '.join([str(n) for n in entry])
        return '{:13s}'.format(entry_str)

    def _find_possible_cards(self, cards: Iterable[Card]) -> List[Card]:
        """Returns all of the given cards that could be part of the solution."""
        possible_cards = []
        for card in cards:
            if self._is_solution(card):
                possible_cards = [card]
                break
            elif self._is_possible(card):
                possible_cards.append(card)
        return possible_cards

    def _is_possible(self, card: Card) -> bool:
        """Checks if a given card could be part of the solution."""
        return not any([entry == self.YES for entry in self._sheet[card]])

    def _is_solution(self, card: Card) -> bool:
        """Checks if a given card is definitely part of the solution."""
        return all([entry == self.NO for entry in self._sheet[card]])

    def _mark_other_shown(self, cards: List[Card], showing_player: str) -> None:
        """Updates the ledger after another player's suggestion is disproved."""

        # Check if showing player has known suggested card
        player_index = self._get_player_index(showing_player)
        already_shown = False
        for card in cards:
            if self._sheet[card][player_index] == self.YES:
                already_shown = True
                break

        # Showing player must have one of the given cards
        if not already_shown:
            disproof_id = self._new_disproof_id(player_index)
            for card in cards:
                if self._sheet[card][player_index] != self.NO:
                    self._sheet[card][player_index].add(disproof_id)

    def _mark_player_shown(self, shown_card: Card, showing_player: str) -> None:
        """Updates the ledger after the player's suggestion is disproved."""
        player_index = self._get_player_index(showing_player)
        self._sheet[shown_card][player_index] = self.YES

    def _get_player_index(self, player_prefix: str) -> int:
        """Finds the numeric index for a player matching the given prefix."""
        for i, value in enumerate(self._all_players):
            if util.is_prefix_match(player_prefix, value):
                return i
        raise ValueError('No player with prefix: ' + player_prefix)

    def _get_disproof_ids(self, player_index: int) -> Set[int]:
        """Gets the IDs of all unresolved suggestions disproved by a player."""
        current_ids: Set[int] = set()
        for card in Card.__members__.values():
            entry = self._sheet[card][player_index]
            if entry not in (self.YES, self.NO):
                current_ids |= entry
        return current_ids

    def _new_disproof_id(self, player_index: int) -> int:
        """Returns an ID representing a new suggestion disproved by a player."""
        current_ids = self._get_disproof_ids(player_index)
        new_id = 1
        while new_id in current_ids:
            new_id += 1
        return new_id

    def _simplify(self) -> None:
        """Tries to simplify the ledger by making deductions about cards."""
        pass
