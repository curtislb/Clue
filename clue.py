#!/usr/bin/env python3

"""clue.py

A note-taking client for the board game Clue. Updates in real time the possible
cards held by all players as suggestions/accusations are made and disproved.
"""

__author__ = 'Curtis Belmonte'

from collections import Counter
from enum import IntEnum
from operator import itemgetter
from typing import Counter as CounterT, Dict, List, Optional, Set


#####################
# Class Definitions
#####################


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
            if is_prefix_match(prefix, name):
                return card
        raise KeyError('No card with prefix: ' + prefix)


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
        self._players = all_players
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
            [' ' * 14] + ['{:13s}'.format(player) for player in self._players]
        )
        divider = '-' * (15 + 16 * len(self._players))
        lines = ['', header, divider]

        # Add line for each game card, with an entry for each player
        for i, row in enumerate(self._sheet):
            row_label = '{:14s}'.format(Card(i).name)
            lines.append(' | '.join(
                [row_label] + [self._format_entry(entry) for entry in row]
            ))

        return '\n'.join(lines)

    def add_suggestion(
            self,
            cards: List[Card],
            passing_players: List[str],
            showing_player: str
    ) -> None:
        """Updates the ledger after a suggestion has been made and disproved."""

        # Passing players can't have any of the given cards
        for player in passing_players:
            for card in cards:
                player_index = self._get_player_index(player)
                self._sheet[card][player_index] = self.NO

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

        # Make any deductions based on new info
        self._simplify()

    def is_possible(self, card: Card) -> bool:
        """Checks if a given card could be part of the solution."""
        return not any([entry == self.YES for entry in self._sheet[card]])

    def is_solution(self, card: Card) -> bool:
        """Checks if a given card is definitely part of the solution."""
        return all([entry == self.NO for entry in self._sheet[card]])

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

    def _get_player_index(self, player_prefix: str) -> int:
        """Finds the numeric index for a player matching the given prefix."""
        for i, value in enumerate(self._players):
            if is_prefix_match(player_prefix, value):
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


class SuggestionCounter(object):
    """Counter that tracks the number of times players have suggested cards."""

    def __init__(self, all_players: List[str]) -> None:
        self._suggestions: Dict[str, CounterT[Card]] = {
            player: Counter() for player in all_players
        }

    def __repr__(self) -> str:
        lines = ['Suggestions:']

        # Show card counts for each player in descending order
        for player, counts in self._suggestions.items():
            if counts:
                lines.append('  {}:'.format(player))
                sorted_counts = sorted(
                    counts.items(),
                    key=itemgetter(1),
                    reverse=True
                )
                for card, count in sorted_counts:
                    lines.append('    {}: {}'.format(card.name, count))

        return '\n'.join(lines)

    def add_suggestion(self, player: str, cards: List[Card]) -> None:
        """Updates player/card counts after a suggestion has been made."""
        player_name = self._get_player_name(player)
        for card in cards:
            self._suggestions[player_name][card] += 1

    def _get_player_name(self, player_prefix: str) -> str:
        """Finds the numeric index for a player matching the given prefix."""
        for player in self._suggestions.keys():
            if is_prefix_match(player_prefix, player):
                return player
        raise ValueError('No player with prefix: ' + player_prefix)


#####################
# Main Program
#####################


def main() -> None:
    # Prompt user for initial game info, including players and cards
    player = input('Enter your name: ').strip()
    opponents = input('Enter opponents: ').strip().split()
    own_cards = [
        Card.parse(s) for s in input('Enter your cards: ').strip().split()
    ]

    # Set up the ledger and global suggestion counts
    all_players = [player] + opponents
    ledger = Ledger(all_players, player, own_cards)
    suggestions = SuggestionCounter(all_players)

    # Main game loop
    while True:
        # Display the current game info
        print(ledger)
        print()
        print(suggestions)
        print()

        # Check if we have a unique solution
        solution = maybe_solve(ledger)
        if solution is not None:
            print('Unique solution found:')
            print(', '.join([card.name for card in solution]))

        # Prompt user to enter relevant info for each suggestion
        suggesting_player, *suggested_card_names = (
            input('Enter suggestion (player cards...): ').strip().split()
        )
        passing_players = input('Enter players passing: ').strip().split()
        showing_player = input('Enter player showing: ').strip()

        # Update ledger and global suggestion counts
        suggested_cards = [Card.parse(name) for name in suggested_card_names]
        ledger.add_suggestion(suggested_cards, passing_players, showing_player)
        suggestions.add_suggestion(suggesting_player, suggested_cards)


#####################
# Utility Functions
#####################


def is_prefix_match(prefix: str, value: str) -> bool:
    """Checks if value has the given case-insensitive prefix."""
    return value.lower().startswith(prefix.lower())


def maybe_solve(ledger: Ledger) -> Optional[List[Card]]:
    """Returns the cards that make up the solution, or None if ambiguous."""

    definite_cards: List[Card] = []
    possible_cards: Optional[List[Card]] = []
    for card in Card.__members__.values():
        # Check for cards that must be part of the solution
        if ledger.is_solution(card):
            definite_cards.append(card)
        if len(definite_cards) == 3:
            possible_cards = definite_cards
            break

        # Check for cards that haven't been ruled out yet
        if possible_cards is not None:
            if ledger.is_possible(card):
                possible_cards.append(card)
            if len(possible_cards) > 3:
                possible_cards = None

    # Only return cards as solution if we have exactly three
    if possible_cards is not None and len(possible_cards) == 3:
        return possible_cards
    else:
        return None


#####################


if __name__ == '__main__':
    main()
