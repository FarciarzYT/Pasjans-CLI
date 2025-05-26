import random
from typing import List, Optional
from .card import Card
from utils.constants import Suit, Rank

class Deck:
    """Reprezentuje talię kart do gry w pasjansa."""

    def __init__(self):
        """Tworzy nową, przetasowaną talię kart."""
        self.cards: List[Card] = self._create_deck()
        self.shuffle()

    def _create_deck(self) -> List[Card]:
        return [Card(suit, rank) for suit in Suit for rank in Rank]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self) -> Optional[Card]:
        """
        Zwraca i usuwa pierwszą kartę z talii.
        Zwraca None, jeśli talia jest pusta.
        """
        return self.cards.pop(0) if not self.is_empty() else None

    def add_cards(self, cards_to_add: List[Card]) -> None:
        """Dodaje karty z powrotem do talii, zazwyczaj w celu przetasowania stosu kart odpadowych do zapasu."""
        self.cards.extend(cards_to_add)

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def __len__(self) -> int:
        return len(self.cards)
    