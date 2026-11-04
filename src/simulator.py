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

    def run(self, strategy: BaseStrategy, strategy_name: str) -> Dict[str,float]:
        """ Executes the simulation loop and batches telemetry to the database. """
        buffer = []
        cumulative_bankroll = 0.0
        start_time = time.time()

        for round_id in range(1, self.config.num_rounds + 1):
            # Dynamic bet sizing for counters, otherwise static base bet
            current_bet = strategy.get_bet_size(self.config.base_bet) if hasattr(strategy, 'get_bet_size') else self.config.base_bet

            # Execute round
            net_payout = self.game.play_round(strategy_agent=strategy, base_bet=current_bet)
            cumulative_bankroll += net_payout

            # Track global values
            self.total_wagered += current_bet
            self.total_payout += net_payout
            self._update_counters(net_payout, current_bet)

            # Log round data for database insertion
            buffer.append({
                "round_id": round_id,
                "strategy_name": strategy_name,
                "bet_amount": current_bet,
                "net_payout": net_payout,
                "cumulative_bankroll": cumulative_bankroll
            })

            # Flush batch to database
            if len(buffer) >= self.config.batch_size:
                self.db.insert_rounds_batch(buffer)
                buffer.clear()

            # Flush remaining
            if buffer:
                self.db.insert_rounds_batch(buffer)

            execution_time = time.time() - start_time
            return self.get_summary_stats(execution_time)

    def _update_counters(self, net_payout: float, bet: float) -> None:
        if net_payout > bet:
            self.results_counter["blackjack"] += 1
        elif net_payout > 0:
            self.results_counter["win"] += 1
        elif net_payout < 0:
            self.results_counter["loss"] += 1
        else:
            self.results_counter["push"] += 1

    def get_summary_stats(self, execution_time: float) -> Dict[str,float]:
        """ Computes metrics post-simulation """
        house_edge = -(self.total_payout/self.total_wagered) if self.total_wagered > 0 else 0.0
        return {
            "house_edge_pct": house_edge * 100,
            "win_rate_pct": (self.results_counter["win"] + self.results_counter["blackjack"]) / self.config.num_rounds * 100,
            "loss_rate_pct": self.results_counter["loss"] / self.config.num_rounds * 100,
            "push_rate_pct": self.results_counter["push"] / self.config.num_rounds * 100,
            "execution_time_sec": execution_time
        }   

    def run_benchmark_suite(strategies: List[BaseStrategy], config: SimulationConfig, db_manager = DatabaseManager) -> None:
        """ Helper to run and compare multiple strategies sequentially """
        for strategy in strategies:
            strategy_name = strategy.__class__.__name__
            simulator = MonteCarloSimulator(config, db_manager)
            stats = simulator.run(strategy, strategy_name)

            print(f"--- {strategy_name} ---")
            print(f"House Edge: {stats['house_edge_pct']:.3f}%")
            print(f"Win Rate:   {stats['win_rate_pct']:.2f}%")
            print(f"Exectuion:  {stats['execution_time_sec']:.2f}s\n")