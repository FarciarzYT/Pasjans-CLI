import random
from typing import List, Optional
from .card import Card
from utils.constants import Suit, Rank

class Deck:
    def __init__(self):
        self.cards: List[Card] = self._create_deck()
        self.shuffle()

    def _create_deck(self) -> List[Card]:
        return [Card(suit, rank) for suit in Suit for rank in Rank]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self) -> Optional[Card]:
        if not self.is_empty():
            return self.cards.pop(0) 
        return None

    def add_cards(self, cards_to_add: List[Card]) -> None:
        """Adds cards back to the deck, usually for reshuffling waste pile to stock."""
        self.cards.extend(cards_to_add)

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def __len__(self) -> int:
        return len(self.cards)