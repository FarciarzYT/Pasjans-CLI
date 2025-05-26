from utils.constants import Suit, Rank, FACE_DOWN_CARD_STR

class Card:
    """Reprezentuje pojedynczą kartę do gry w pasjansa."""
    def __init__(self, suit: Suit, rank: Rank, face_up: bool = False):
        if not isinstance(suit, Suit):
            raise TypeError(f"suit must be an instance of Suit, got {type(suit)}")
        if not isinstance(rank, Rank):
            raise TypeError(f"rank must be an instance of Rank, got {type(rank)}")
        self.suit = suit
        self.rank = rank
        self.face_up = face_up

    @property
    def color(self):
        return self.suit.color

    @property
    def value(self):
        return self.rank.value

    def flip(self):
        """Odwraca stan karty (face up/down)."""
        self.face_up = not self.face_up

    def __str__(self):
        if not self.face_up:
            return FACE_DOWN_CARD_STR
        return f"{self.rank.symbol}{self.suit.value}"

    def __repr__(self):
        return f"Card({self.suit.name}, {self.rank.name}, face_up={self.face_up})"

    def __hash__(self):
        return hash((self.suit, self.rank, self.face_up))

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.rank == other.rank and self.face_up == other.face_up

    def is_next_rank_for_tableau(self, other_card: 'Card') -> bool:
        return self.rank.value == other_card.rank.value - 1

    def is_next_rank_for_foundation(self, other_card: 'Card') -> bool:
        return self.rank.value == other_card.rank.value + 1
    