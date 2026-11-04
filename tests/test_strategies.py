import pytest
from src.engine import Card, Hand, Shoe, BlackjackGame, Action
from src.strategies.base import BaseStrategy

# Test strategies for mocking

class StandOnFirstActionStrategy(BaseStrategy):
    """ Deterministic dummy strategy that always stands immediately """
    def get_action(self, player_hand: Hand, dealer_upcard: Card, **kwargs) -> Action:
        return Action.STAND

class AlwaysDoubleStrategy(BaseStrategy):
    """ Deterministic dummy strategy that always attempts to double """
    def get_action(self, player_hand: Hand, dealer_upcard: Card, **kwargs):
        return Action.DOUBLE

# Fixtures

@pytest.fixture
def empty_hand():
    return Hand()

@pytest.fixture
def standard_shoe():
    return Shoe(num_decks=6, penetration=0.75)

# Hand Valuation and Ace Mechanics Tests

def test_hand_numeric_sum(empty_hand):
    empty_hand.add_card(Card("8","SPADE"))
    empty_hand.add_card(Card("7","DIAMOND"))
    assert empty_hand.total == 15
    assert not empty_hand.is_soft
    assert not empty_hand.is_bust

def test_hand_face_cards_value(empty_hand):
    empty_hand.add_card(Card("K","CLUB"))
    empty_hand.add_card(Card("Q","HEART"))
    assert empty_hand.total == 20
    assert not empty_hand.is_soft

def test_soft_hand_with_single_ace(empty_hand):
    empty_hand.add_card(Card("A","SPADE"))
    empty_hand.add_card(Card("7","DIAMOND"))
    assert empty_hand.total == 18
    assert empty_hand.is_soft

def test_ace_downgrades_to_prevent_bust(empty_hand):
    empty_hand.add_card(Card("A","SPADE"))
    empty_hand.add_card(Card("8","DIAMOND"))
    assert empty_hand.total == 19
    assert empty_hand.is_soft

    # Adding a 5 forces ace to convert 11 -> 1
    empty_hand.add_card(Card("5","CLUB"))
    assert empty_hand.total == 14
    assert not empty_hand.is_soft
    assert not empty_hand.is_bust

def test_multiple_aces_resolution(empty_hand):
    empty_hand.add_card(Card("A","SPADE"))
    empty_hand.add_card(Card("A","DIAMOND"))
    empty_hand.add_card(Card("9","HEART"))
    # One ace counts as 11, the other as 1, 11 + 9 + 1 = 21
    assert empty_hand.total == 21
    assert empty_hand.is_soft

    # Adding another card converts the remaining 11 to 1, 1 + 1 + 9 + 5 = 16
    empty_hand.add_card(Card("5","CLUB"))
    assert empty_hand.total == 16
    assert not empty_hand.is_soft

def test_bust_detection(empty_hand):
    empty_hand.add_card(Card("10", "SPADE"))
    empty_hand.add_card(Card("9", "DIAMOND"))
    empty_hand.add_card(Card("5", "CLUB"))
    assert empty_hand.total == 24
    assert empty_hand.is_bust

# Shoe and Penetration Mechanics Tests