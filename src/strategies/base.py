from abc import ABC, abstractmethod
from typing import Any

from src.engine import Action, Hand, Card

class BaseStrategy(ABC):
    """
    Abstract base class for all blackjack strategues.
    Ensures a uniform interface for the Monte Carlo Simulation and multi-agent environments
    """

    @abstractmethod
    def get_action(self, player_hand: Hand, dealer_upcard: Card, **kwargs: Any) -> Action:
        """
        Determines the optimal action to take given the current game

        Args:
            player_hand: The current Hand object of the player
            dealer_upcard: The visible face-up Card object of the dealer
            **kwargs: Additional contextual state (e.g. true_count, deck_penetration or PyTorch tensor states)

        Returns:
            An Action enum (e.g. Action.HIT, Action.STAND).
        """
        pass
    
    def get_bet_size(self, base_bet: float, **kwargs: Any) -> float:
        """
        Determine the bet size for the upcoming game.
        Defaults to a static base bet, dynamic strategies should override this method.
        
        Args: 
            base_bet: The standard unit configured in the simulation.
            **kwargs: Additional context

        Returns:
            The final float amount to wager
        """
        return base_bet

    def observe_card(self, card: Card) -> None:
        """
        Optional hook for strategies that need to track state across the entire shoe.
        Card counting agents should override this to update their running total.
        """
        pass

    def reset_shoe(self) -> None:
        """
        Optional hook triggered when the dealer shuffles the shoe.
        Card counting agents should override this to reset their running total.
        """
        pass