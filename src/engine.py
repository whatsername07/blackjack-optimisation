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

    