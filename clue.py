#!/usr/bin/env python3

"""clue.py

A note-taking client for the board game Clue. Updates in real time the possible
cards held by all players as suggestions/accusations are made and disproved.
"""

__author__ = 'Curtis Belmonte'

import traceback

from deduction import Ledger, SuggestionTracker
from pieces import Card


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
    suggestions = SuggestionTracker(all_players)

    # Main game loop
    while True:
        # Display the current game info
        print(ledger)
        print()
        print(suggestions)
        print()

        # Check if we have a unique solution
        solution = ledger.solve()
        if solution is not None:
            print('*** Unique solution found! ***')
            print(', '.join([card.name for card in solution]))

        # noinspection PyBroadException
        try:
            process_input(player, ledger, suggestions)
        except Exception:
            print('Whoops! Something went wrong:')
            traceback.print_exc()


def process_input(
    player: str,
    ledger: Ledger,
    suggestions: SuggestionTracker
) -> None:
    """Updates the current known game state based on user input."""

    # Prompt user to enter relevant info for each suggestion
    suggesting_player, *suggested_card_names = (
        input('Enter suggestion (player first): ').strip().split()
    )
    passing_players = input('Enter players passing: ').strip().split()
    showing_player = input('Enter player showing: ').strip()

    # Update ledger and suggestion info
    suggested_cards = [Card.parse(name) for name in suggested_card_names]
    ledger.add_suggestion(suggested_cards, passing_players, showing_player)
    suggestions.add(suggesting_player, suggested_cards, showing_player)


if __name__ == '__main__':
    main()
