#!/usr/bin/env python3

"""clue.py

A note-taking client for the board game Clue. Updates in real time the possible
cards held by all players as suggestions/accusations are made and disproved.
"""

__author__ = 'Curtis Belmonte'

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
    shown_cards = ShownCardTracker(opponents)
    skipped_cards = SkippedCardTracker()
    suggestions = SuggestionTracker(all_players)

    # Main game loop
    while True:
        # Display the current game info
        for info in (shown_cards, skipped_cards, suggestions, ledger):
            print(info)
            print()

        # Check if we have a unique solution
        solution = ledger.solve()
        if solution is not None:
            print('*** Unique solution found! ***')
            print(', '.join([card.name for card in solution]))
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
    suggesting_prefix, *suggested_card_prefixes = (
        input('Enter suggestion: ').strip().split()
    )
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
    suggestions.update(suggesting_player, suggested_cards, showing_player)
    if player in passing_players:
        skipped_cards.update(suggested_cards)


if __name__ == '__main__':
    main()
