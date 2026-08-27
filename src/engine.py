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