#!/usr/bin/env python3

"""ledger.py

Provides a ledger class for keeping notes and making deductions about the cards
that players hold and, by extension, the cards that make up the solution.
"""

__author__ = 'Curtis Belmonte'

import itertools
from collections import defaultdict
from typing import DefaultDict, Iterable, List, Optional, Set, Tuple

from pieces import Card, ROOMS, SUSPECTS, WEAPONS


class Ledger(object):
    """Spreadsheet with information about players and their cards."""

    # Ledger entries with special meaning
    YES = {-1}  # player has card
    NO = {-2}   # player doesn't have card

    def __init__(
        self,
        all_players: List[str],
        hand_sizes: List[int],
        player: str,
        own_cards: List[Card]
    ) -> None:

        # Ensure user-supplied params are logically consistent
        assert len(all_players) == len(hand_sizes)
        assert player in all_players
        assert hand_sizes[all_players.index(player)] == len(own_cards)

        self._all_players = all_players
        self._player = player
        self._hand_sizes = hand_sizes
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
        lines = [header]

        # Add line for each game card, with an entry for each player
        divider = '-' * (15 + 16 * len(self._all_players))
        for category in (SUSPECTS, WEAPONS, ROOMS):
            lines.append(divider)
            for card in category:
                row_label = self._format_card(card)
                lines.append(' | '.join(
                    [row_label]
                    + [self._format_entry(entry) for entry in self._sheet[card]]
                ))

        return '\n'.join(lines)

    def solve(self) -> Optional[Tuple[Card, Card, Card]]:
        """Returns the cards that make up the solution, or None if ambiguous."""
        suspects = self._find_possible_cards(SUSPECTS)
        weapons = self._find_possible_cards(WEAPONS)
        rooms = self._find_possible_cards(ROOMS)
        if len(suspects) == 1 and len(weapons) == 1 and len(rooms) == 1:
            solution: Optional[Tuple[Card, Card, Card]] = (
                suspects[0],
                weapons[0],
                rooms[0],
            )
        else:
            solution = None
        return solution

    def update(
        self,
        cards: List[Card],
        passing_players: List[str],
        showing_player: Optional[str],
        shown_card: Optional[Card]
    ) -> None:
        """Updates the ledger after a suggestion has been made and disproved."""

        # Passing players can't have any of the given cards
        for player in passing_players:
            for card in cards:
                player_index = self._get_player_index(player)
                self._mark_no(card, player_index)

        # Update ledger based on showing player and/or shown card
        if showing_player is not None:
            if shown_card is None:
                self._mark_other_shown(cards, showing_player)
            elif not showing_player == self._player:
                self._mark_player_shown(shown_card, showing_player)

        # Make any deductions based on new info
        self._simplify()

    def _format_card(self, card: Card) -> str:
        """Converts a card into a string that can be used as a row label."""
        if self._is_solution(card):
            card_str = '*{}*'.format(card.name)
        elif not self._is_possible(card):
            card_str = '-{}-'.format(card.name)
        else:
            card_str = card.name
        return '{:14s}'.format(card_str)

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

    def _mark(self, card: Card, player_index: int, value: Set[int]) -> None:
        """Updates the ledger entry for the given card and player to value."""
        if value == self.NO:
            self._mark_no(card, player_index)
        elif value == self.YES:
            self._mark_yes(card, player_index)
        else:
            self._sheet[card][player_index] = value

    def _mark_no(self, card: Card, player_index: int) -> None:
        """Updates the ledger entry for the given card and player to NO."""
        self._sheet[card][player_index] = self.NO

    def _mark_yes(self, card: Card, player_index: int) -> None:
        """Updates the ledger entry for the given card and player to YES."""

        # Clean up disproved suggestions now that we know player has card
        disproof_ids = self._sheet[card][player_index]
        for c in Card.__members__.values():
            if c != card:
                self._sheet[c][player_index] = (
                    self._sheet[c][player_index] - disproof_ids
                )

        self._sheet[card][player_index] = self.YES

    def _fill_column(self, col: int, value: Set[int]) -> bool:
        """Fills all unknown entries in the given column with a given value.

        Any entry other than YES or NO is considered "unknown". Returns True if
        any entries in the column were reassigned, or False otherwise.
        """
        did_change = False
        for c in Card.__members__.values():
            if self._sheet[c][col] not in (self.YES, self.NO):
                self._mark(c, col, value)
                did_change = True
        return did_change

    def _fill_row(self, row: int, value: Set[int]) -> bool:
        """Fills all unknown entries in the given row with a given value.

        Any entry other than YES or NO is considered "unknown". Returns True if
        any entries in the row were reassigned, or False otherwise.
        """
        did_change = False
        for p in range(len(self._all_players)):
            if self._sheet[row][p] not in (self.YES, self.NO):
                self._mark(Card(row), p, value)
                did_change = True
        return did_change

    def _find_possible_cards(self, cards: Iterable[Card]) -> List[Card]:
        """Returns all of the given cards that could be part of the solution."""
        possible_cards: List[Card] = []
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
        self._mark_yes(shown_card, player_index)

    def _get_player_index(self, player: str) -> int:
        """Finds the numeric index for a player with the given name."""
        for i, value in enumerate(self._all_players):
            if player == value:
                return i
        raise ValueError('No player with name: ' + player)

    def _get_disproof_id_map(
        self,
        player_index: int
    ) -> DefaultDict[int, Set[Card]]:
        """Gets the IDs of all unresolved suggestions disproved by a player.

        Returns a dict mapping each unique ID to the set of cards that it is
        still associated with for a given player.
        """
        disproof_id_map: DefaultDict[int, Set[Card]] = defaultdict(set)
        for card in Card.__members__.values():
            entry = self._sheet[card][player_index]
            if entry not in (self.YES, self.NO):
                for disproof_id in entry:
                    disproof_id_map[disproof_id].add(card)
        return disproof_id_map

    def _new_disproof_id(self, player_index: int) -> int:
        """Returns an ID representing a new suggestion disproved by a player."""
        current_ids = set(self._get_disproof_id_map(player_index).keys())
        new_id = 1
        while new_id in current_ids:
            new_id += 1
        return new_id

    def _simplify(self) -> None:
        """Tries to simplify the ledger by making deductions about cards."""
        did_change = True
        while did_change:
            did_change = any((
                self._simplify_known_holders(),
                self._simplify_max_no_counts(),
                self._simplify_max_yes_counts(),
                self._simplify_solved_categories(),
                self._simplify_single_possibilities(),
                self._simplify_single_shown_cards(),
                self._simplify_sufficient_shown_cards(),
            ))

    def _simplify_known_holders(self) -> bool:
        """Simplifies ledger by applying a "single holder" rule for each card.

        Specifically, for each card that we have marked as being held by a
        player, marks all other players as not holding that card.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """
        did_change = False
        for i, row in enumerate(self._sheet):
            for j, entry in enumerate(row):
                if entry == self.YES:
                    # Mark NO for all other players in this row
                    did_change = self._fill_row(i, self.NO) or did_change
                    break
        return did_change

    def _simplify_max_no_counts(self) -> bool:
        """Simplifies ledger by applying a "max NO count" rule for each player.

        Specifically, for each player that we have marked as not having a number
        of cards equal to total_cards - (hand_size - yes_count), marks the
        player as having all of the remaining cards.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """

        did_change = False
        num_cards = len(self._sheet)
        for p in range(len(self._all_players)):
            # Count NO entries in player's column
            no_count = 0
            for i in range(num_cards):
                if self._sheet[i][p] == self.NO:
                    no_count += 1

            # If NO count is max possible, make all other column entries YES
            if no_count >= num_cards - self._hand_sizes[p]:
                did_change = self._fill_column(p, self.YES) or did_change

        return did_change

    def _simplify_max_yes_counts(self) -> bool:
        """Simplifies ledger by applying a "max YES count" rule for each player.

        Specifically, for each player that we have marked as having a number of
        cards equal to hand_size, marks that player as not having all of the
        remaining cards.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """

        did_change = False
        for p in range(len(self._all_players)):
            # Count YES entries in player's column
            yes_count = 0
            for c in Card.__members__.values():
                if self._sheet[c][p] == self.YES:
                    yes_count += 1

            # If YES count is max possible, make all other column entries NO
            if yes_count >= self._hand_sizes[p]:
                did_change = self._fill_column(p, self.NO) or did_change

        return did_change

    def _simplify_solved_categories(self) -> bool:
        """Simplifies ledger by applying a "solved category" rule for all cards.

        Specifically, if we know which card in a category (suspects, weapons, or
        rooms) is part of the solution, and any of the other cards in that
        category can only be held by one player, marks those entries as YES.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """
        did_change = False
        for category in (SUSPECTS, WEAPONS, ROOMS):
            did_change = self._simplify_solved_category(category) or did_change
        return did_change

    def _simplify_solved_category(self, category: Iterable[Card]) -> bool:
        """Simplifies ledger by applying a "solved category" rule for category.

        Specifically, if we know a card in category is part of the solution, and
        any of the other cards in category can only be held by one player, marks
        the corresponding entries as YES.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """

        did_change = False

        # Look for a card that is a known part of the solution
        solution_card: Optional[Card] = None
        for card in category:
            if self._is_solution(card):
                solution_card = card
                break

        if solution_card is not None:
            for card in category:
                # No need to simplify row with solution card
                if card == solution_card:
                    continue

                # Find index of only possible owner, if any
                owner_index: Optional[int] = None
                for p in range(len(self._all_players)):
                    if self._sheet[card][p] == self.YES:
                        # Card already has known owner
                        owner_index = None
                        break
                    elif self._sheet[card][p] != self.NO:
                        if owner_index is None:
                            owner_index = p
                        else:
                            owner_index = None
                            break

                # Mark only possible owner as holding card
                if owner_index is not None:
                    self._mark_yes(card, owner_index)
                    did_change = True

        return did_change

    def _simplify_single_possibilities(self) -> bool:
        """Simplifies ledger by applying a "1 possibility" rule for all cards.

        Specifically, if we know all cards in a category (suspects, weapons, or
        rooms) except for one are held by other players, marks the remaining
        card as not held by any player, since it must be part of the solution.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """
        did_change = False
        for category in (SUSPECTS, WEAPONS, ROOMS):
            did_change = self._simplify_single_possible(category) or did_change
        return did_change

    def _simplify_single_possible(self, category: Iterable[Card]) -> bool:
        """Simplifies ledger by applying a "1 possibility" rule for category.

        Specifically, if we know all cards in category except for one are held
        by other players, marks the remaining card as not held by any player.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """
        did_change = False
        possible_cards = self._find_possible_cards(category)
        if len(possible_cards) == 1:
            did_change = self._fill_row(possible_cards[0], self.NO)
        return did_change

    def _simplify_single_shown_cards(self) -> bool:
        """Simplifies ledger by applying a "1 shown card" rule for each player.

        Specifically, if there is only one possible card left for a suggestion
        that a player has disproved, marks that player as having the card.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """
        did_change = False
        for player_index in range(len(self._all_players)):
            disproof_id_map = self._get_disproof_id_map(player_index)
            for cards in disproof_id_map.values():
                if len(cards) == 1:
                    self._mark_yes(list(cards)[0], player_index)
                    did_change = True
        return did_change

    def _simplify_sufficient_shown_cards(self) -> bool:
        """Simplifies ledger by applying a "sufficient shown cards" rule.

        Specifically, for each player that has a sufficient spread of possible
        shown cards from suggestions they have disproved to account for all
        cards in their hand, marks all other cards as NO.

        Returns True if the ledger changes as a result of applying this rule, or
        False if the ledger is unchanged.
        """
        did_change = False
        for player_index in range(len(self._all_players)):
            if self._has_sufficient_shown_cards(player_index):
                for c in Card.__members__.values():
                    if not self._sheet[c][player_index]:
                        self._mark_no(c, player_index)
                        did_change = True
        return did_change

    def _has_sufficient_shown_cards(self, player_index: int) -> bool:
        """Checks if a player satisfies the "sufficient shown cards" rule."""

        # Count number of cards we already know player has
        yes_count = 0
        for c in Card.__members__.values():
            if self._sheet[c][player_index] == self.YES:
                yes_count += 1

        # Check if shown cards cover their remaining cards
        is_sufficient = True
        hand_size = self._hand_sizes[player_index]
        if yes_count < hand_size:
            possible_seqs: Iterable[Iterable[Card]] = itertools.product(
                *(self._get_disproof_id_map(player_index).values())
            )
            for shown_seq in possible_seqs:
                if len(set(shown_seq)) < hand_size - yes_count:
                    is_sufficient = False
                    break

        return is_sufficient
