# Blackjack game engine

from enum import Enum
import random
from typing import List, Tuple

class Action(Enum):
    STAND = 0
    HIT = 1
    DOUBLE = 2
    SPLIT = 3