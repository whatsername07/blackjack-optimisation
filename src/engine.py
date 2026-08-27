# Blackjack game engine

from enum import Enum
import random
from typing import List, Tuple

class Action(Enum):
    STAND = 0
    HIT = 1
    DOUBLE = 2
    SPLIT = 3

class Card:
    """Represents a single card with rank, suit and point value"""

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit
        if rank in ["J","Q","K"]:
            self.value = 10
        elif rank == "A":
            self.value = 11
        else:
            self.value = int(rank)
        pass

class Shoe:
    """Manages multi-deck shoe creation, shuffling and penetration threshold"""
    def __init__(self, num_decks: int = 6, penetration: float = 0.75):
        self.num_decks = num_decks
        self.penetration = penetration
        self.cards: List[Card] = []
        self.cut_card_reached = False
        self.reset_and_shuffle()

    def reset_and_shuffle(self) -> None:
        ranks = [str(n) for n in range(2,11)] + ["J","Q","K","A"]
        suits = ["♠", "♥", "♦", "♣"]
        self.cards = [Card(r,s) for _ in range(self.num_decks) for s in suits for r in ranks]
        random.shuffle(self.cards)
        self.cut_card_index = int(len(self.cards) * (1-self.penetration))
        self.cut_card_reached = False

    def deal_card(self) -> Card:
        if len(self.cards) <= self.cut_card_index:
            self.cut_card_reached = True
        return self.cards.pop()

class Hand:
    """Dynamically calculates hand totals and tracks soft ace conversions"""
    def __init__(self):
        self.cards: List[Card] = []

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    @property
    def value_and_softness(self) -> Tuple[int, bool]:
        """Returns (best_total, is_soft), Converts aces from 11 to 1 to prevent busting"""
        total = sum(c.value for c in self.cards)
        num_aces = sum(1 for c in self.cards if c.rank == "A")

        # downgrade aces from 11 to 1 as needed
        while total > 21 and num_aces > 0:
            total -= 10
            num_aces -= 1

        is_soft = num_aces >0 and total <= 21
        return total, is_soft

    @property
    def total(self) -> int:
        return self.value_and_softness[0]

    @property
    def is_soft(self) -> bool:
        return self.value_and_softness[1]

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.total == 21

    @property
    def is_bust(self) -> bool:
        return self.total > 21

