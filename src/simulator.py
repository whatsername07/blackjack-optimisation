import time
import random
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

from src.engine import Shoe, BlackjackGame
from src.db import DatabaseManager
from src.strategies.base import BaseStrategy

@dataclass
class SimulationConfig:
    num_rounds: int = 100_000
    base_bet: float = 1.0
    num_decks: int = 6
    penetration: float = 0.75
    seed: int = 67
    batch_size: int = 10_000

class MonteCarloSimulator:
    def __init__(self, config: SimulationConfig, db_manager: DatabaseManager):
        self.config = config
        self.db = db_manager

        # Enforce reproducibility
        random.seed(self.config.seed)
        np.random.seed(self.config.seed)

        self.shoe = Shoe(num_decks=self.config.num_decks, penetration=self.config.penetration)
        self.game = BlackjackGame(shoe=self.shoe)

        # Telemetry state
        self.total_wagered = 0.0
        self.total_payout = 0.0
        self.results_counter = {"win": 0, "loss": 0, "push": 0, "blackjack": 0}

    