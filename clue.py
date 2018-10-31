#!/usr/bin/env python3

"""clue.py

A note-taking client for the board game Clue. Updates in real time the possible
cards held by all players as suggestions/accusations are made and disproved.
"""

__author__ = 'Curtis Belmonte'

import sys
import traceback
from typing import List, Optional

import prefix
from ledger import Ledger
from pieces import Card
from trackers import ShownCardTracker, SkippedCardTracker, SuggestionTracker


def main() -> None:
    # Prompt user for initial game info, including players and cards
    player = input('Enter your name: ').strip()
    opponents = input('Enter opponents: ').strip().split()
    own_cards = [
        Card.parse(s) for s in input('Enter your cards: ').strip().split()
    ]

    # Prompt for opponents' hand sizes if necessary
    hand_sizes = [len(own_cards)]
    card_count = len(Card.__members__)
    player_count = 1 + len(opponents)
    if (card_count - 3) % player_count != 0:
        for opponent in opponents:
            hand_sizes.append(
                int(input('Enter hand size for {}: '.format(opponent)).strip())
            )
    else:
        hand_sizes *= player_count

    # Set up the ledger and card/suggestion trackers
    all_players = [player] + opponents
    ledger = Ledger(all_players, hand_sizes, player, own_cards)
    suggestions = SuggestionTracker()
    shown_cards = ShownCardTracker(opponents)
    skipped_cards = SkippedCardTracker()

    # Main game loop
    while True:
        # Display the current game info
        print()
        print('#' * 79)
        print()
        for info in (suggestions, shown_cards, skipped_cards, ledger):
            print(info)
            print()

        # Check if we have a unique solution
        solution = ledger.solve()
        if solution is not None:
            print('******************************')
            print('*** Unique solution found! ***')
            print('******************************')
            print(', '.join(card.name for card in solution))
            print()

        # noinspection PyBroadException
        try:
            process_input(
                player,
                all_players,
                ledger,
                shown_cards,
                skipped_cards,
                suggestions
            )
        except Exception:
            print()
            print('Whoops! Something went wrong...')
            traceback.print_exc()
            print()
            response = input('Continue playing? [Y/n] ')
            if prefix.is_match('n', response):
                sys.exit(1)


def process_input(
    player: str,
    all_players: List[str],
    ledger: Ledger,
    shown_cards: ShownCardTracker,
    skipped_cards: SkippedCardTracker,
    suggestions: SuggestionTracker
) -> None:
    """Updates the current known game state based on user input."""

    # Prompt user to enter relevant info for each suggestion
    suggesting_prefix = input('Enter suggesting player: ').strip()
    suggested_card_prefixes = input('Enter suggested cards: ').strip().split()
    passing_prefixes = input('Enter players passing: ').strip().split()
    showing_prefix = input('Enter player showing: ').strip()

    # Map prefixes to actual players/cards
    suggesting_player = prefix.find_match(suggesting_prefix, all_players)
    suggested_cards = [Card.parse(name) for name in suggested_card_prefixes]
    passing_players = [
        prefix.find_match(name, all_players) for name in passing_prefixes
    ]
    showing_player = (
        None if showing_prefix == '' else
        prefix.find_match(showing_prefix, all_players)
    )

    # Handle cases where user is directly involved in suggestion
    shown_card: Optional[Card] = None
    if (
        showing_player is not None
        and player in (suggesting_player, showing_player)
    ):
        shown_card = Card.parse(input('Enter shown card: ').strip())
        if player == showing_player:
            shown_cards.update(suggesting_player, shown_card)

    # Update ledger and suggestion/card trackers
    ledger.update(suggested_cards, passing_players, showing_player, shown_card)
    suggestions.update(
        suggesting_player,
        suggested_cards,
        passing_players,
        showing_player
    )
    if player in passing_players:
        skipped_cards.update(suggested_cards)


if __name__ == '__main__':
    main()
