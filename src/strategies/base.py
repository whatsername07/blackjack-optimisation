from abc import ABC, abstractmethod
from typing import Any

from src.engine import Action, Hand, Card

class BaseStrategy(ABC):
    """
    Abstract base class for all blackjack strategues.
    Ensures a uniform interface for the Monte Carlo Simulation and multi-agent environments
    """