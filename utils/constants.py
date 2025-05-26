from enum import Enum

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    SPADES = "♠"
    CLUBS = "♣"

    @property
    def color(self):
        if self in (Suit.HEARTS, Suit.DIAMONDS):
            return "RED"
        else:
            return "BLACK"

class Rank(Enum):
    ACE = ("A", 1)
    TWO = ("2", 2)
    THREE = ("3", 3)
    FOUR = ("4", 4)
    FIVE = ("5", 5)
    SIX = ("6", 6)
    SEVEN = ("7", 7)
    EIGHT = ("8", 8)
    NINE = ("9", 9)
    TEN = ("10", 10)
    JACK = ("J", 11)
    QUEEN = ("Q", 12)
    KING = ("K", 13)

    def __init__(self, symbol, value):
        self._symbol = symbol
        self._value = value

    @property
    def symbol(self):
        return self._symbol

    @property
    def value(self):
        return self._value

    @classmethod
    def from_value(cls, value):
        for rank in cls:
            if rank.value == value:
                return rank
        raise ValueError(f"No rank with value {value}")

    @classmethod
    def from_symbol(cls, symbol):
        for rank in cls:
            if rank.symbol.upper() == symbol.upper():
                return rank
        raise ValueError(f"No rank with symbol {symbol}")


SUIT_SYMBOLS = {suit: suit.value for suit in Suit}
RANK_SYMBOLS = {rank: rank.symbol for rank in Rank}

PILE_STOCK = 'S'
PILE_WASTE = 'W'
PILE_FOUNDATION = 'F'
PILE_TABLEAU = 'T'    
DIFFICULTY_EASY = "easy"
DIFFICULTY_HARD = "hard"
NUM_TABLEAU_PILES = 7
NUM_FOUNDATION_PILES = 4
MAX_UNDO_MOVES = 3
FACE_DOWN_CARD_STR = "[XX]"
EMPTY_PILE_STR = "[  ]"