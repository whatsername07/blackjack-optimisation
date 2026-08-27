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

class BlackjackGame:
    """Coordinates one round of play between the dealer and agent"""

    def __init__(self, shoe: Shoe, hit_soft_17: bool = False):
        self.shoe = shoe
        self.hit_soft_17 = hit_soft_17

        def play_round(self, strategy_agent, base_bet: float=1.0) -> float:
            """Executes a complete round and returns the net unit profit/loss"""
            if self.shoe.cut_card_reached:
                self.shoe.reset_and_shuffle()

            player_hand = Hand()
            dealer_hand = Hand()

            # Initial 2 card deal
            player_hand.add_card(self.shoe.deal_card())
            dealer_hand.add_card(self.shoe.deal_card())
            player_hand.add_card(self.shoe.deal_card())
            dealer_hand.add_card(self.shoe.deal_card())

            dealer_upcard = dealer_hand.cards[0]

            # check natural blackjacks
            if player_hand.is_blackjack:
                if dealer_hand.is_blackjack:
                    return 0.0 # push
                return 1.5*base_bet # standard 3:2 payout

            if dealer_hand.is_blackjack:
                return -1.0*base_bet

            # player turn
            current_bet = base_bet
            while not player_hand.is_bust:
                action = strategy_agent.get_action(player_hand, dealer_upcard)

                if action == Action.STAND:
                    break
                elif action == Action.HIT:
                    player_hand.add_card(self.shoe.deal_card())
                elif action == Action.DOUBLE:
                    current_bet *= 2.0
                    player_hand.add_card(self.shoe.deal_card())
                    break # doubling receives exactly one card and ends turn

            if player_hand.is_bust:
                return -current_bet

            while True:
                total = dealer_hand.total
                is_soft = dealer_hand.is_soft

                if total < 17 or (self.hit_soft_17 and total == 17 and is_soft):
                    dealer_hand.add_card(self.shoe.deal_card())
                else:
                    break

            # resolve payout
            dealer_total = dealer_hand.total
            player_total = player_hand.total

            if dealer_hand.is_bust or player_total > dealer_total:
                return current_bet
            elif player_total < dealer_total:
                return -current_bet
            else:
                return 0.0