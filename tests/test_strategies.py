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

def test_shoe_card_count(standard_shoe):
    assert len(standard_shoe.cards) == 6*52

def test_cut_card_penetration_flag():
    shoe = Shoe(num_decks=1, penetration=0.5)
    # Deal out over 50% of the 52 cards
    for _ in range(27):
        shoe.deal_card()
    assert shoe.cut_card_reached is True

def test_shoe_resets_and_shuffles(standard_shoe):
    # Drain half the cards
    for _ in range(156):
        standard_shoe.deal_card()
    assert len(standard_shoe.cards) == 156

    standard_shoe.reset_and_shuffle()
    assert len(standard_shoe.cards) == 312
    assert standard_shoe.cut_card_reached is False

# Game Outcomes and Payout Assertions

def test_natural_blackjack_payout(monkeypatch):
    """ Player gets A + K, Dealer gets 10 + 8 -> Standard 3:2 payout (+1.5) """
    shoe = Shoe(num_decks=1)

    # Mock dealing order, P D P D
    mock_cards = [
        Card("8","DIAMOND"),
        Card("K", "CLUB"),
        Card("10", "SPADE"),
        Card("A", "SPADE")
    ]
    # Patch the deal_card method to return our mock cards in order
    monkeypatch.setattr(shoe, "deal_card", lambda: mock_cards.pop())

    game = BlackjackGame(shoe=shoe)
    dummy_strategy = StandOnFirstActionStrategy()

    payout = game.play_round(dummy_strategy, base_bet=10.0)
    assert payout == 15.0

def test_player_bust_immediate_loss(monkeypatch):
    """ Player busts, dealer also would have busted -> Player still loses (dealer advantage) """
    shoe = Shoe(num_decks=1)

    # Hand sequence setup
    cards = [
        Card("10", "SPADE"),
        Card("5", "DIAMOND"),
        Card("6", "CLUB"),
        Card("6", "HEART"),
        Card("10", "DIAMOND")
    ]

    # Reverse so pop() serves in correct order
    cards.reverse()
    monkeypatch.setattr(shoe, "deal_card", lambda: cards.pop())

    class AlwaysHitOnceStrategy(BaseStrategy):
        def __init__(self):
            self.hit_count = 0
        def get_action(self, player_hand: Hand, dealer_upcard: Card, **kwargs) -> Action:
            if self.hit_count == 0:
                self.hit_count += 1
                return Action.HIT
            return Action.STAND

    game = BlackjackGame(shoe=shoe)
    payout = game.play_round(AlwaysHitOnceStrategy(), base_bet=10.0)
    assert payout == -10.0

def test_double_down_doubles_wager(monkeypatch):
    """ Doubling down doubles the original stake and awards exactly one card. """
    shoe = Shoe(num_decks=1)

    cards = [
        Card("5", "SPADE"),
        Card("6", "DIAMOND"),
        Card("6", "CLUB"),
        Card("10", "HEART"),
        Card("9", "SPADE"),
        Card("10", "DIAMOND")
    ]
    cards.reverse()
    monkeypatch.setattr(shoe, "get_card", lambda: cards.pop())

    game = BlackjackGame(shoe=shoe)
    payout = game.play_round(AlwaysDoubleStrategy(), base_bet=10.0)
    assert payout == 20.0