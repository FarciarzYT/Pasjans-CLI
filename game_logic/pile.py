from typing import List, Optional, Union
from .card import Card
from utils.constants import (
    Suit, Rank, FACE_DOWN_CARD_STR, EMPTY_PILE_STR,
    DIFFICULTY_HARD, DIFFICULTY_EASY
)

class Pile:
    def __init__(self):
        self.cards: List[Card] = []

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def add_cards(self, cards_to_add: List[Card]) -> None:
        self.cards.extend(cards_to_add)

    def remove_top_card(self) -> Optional[Card]:
        if not self.is_empty():
            return self.cards.pop()
        return None

    def remove_cards_from_top(self, num_cards: int) -> List[Card]:
        if len(self.cards) >= num_cards > 0:
            removed = self.cards[-num_cards:]
            self.cards = self.cards[:-num_cards]
            return removed
        return []

    def peek_top_card(self) -> Optional[Card]:
        if not self.is_empty():
            return self.cards[-1]
        return None

    def peek_cards_from_top(self, num_cards: int) -> List[Card]:
        if num_cards <= 0:
            return []
        return self.cards[-num_cards:]

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def __len__(self) -> int:
        return len(self.cards)

    def __str__(self) -> str:
        if self.is_empty():
            return EMPTY_PILE_STR
        top_card = self.peek_top_card()
        return str(top_card) if top_card else EMPTY_PILE_STR
    
    def get_all_cards_and_clear(self) -> List[Card]:
        all_cards = list(self.cards) 
        self.cards.clear()
        return all_cards

class StockPile(Pile):
    def __str__(self) -> str:
        if self.is_empty():
            return EMPTY_PILE_STR
        return f"[S:{len(self.cards)}]" 

class WastePile(Pile):
    def get_display_cards(self, difficulty: str) -> List[Card]:
        """Returns cards to display based on difficulty (top 1 or top 3)."""
        if self.is_empty():
            return []
        if difficulty == DIFFICULTY_HARD:
            return self.cards[-3:] 
        else: 
            return self.cards[-1:] 

    def get_playable_card(self) -> Optional[Card]:
        """In both easy and hard, only the actual top card of waste is playable."""
        return self.peek_top_card()

    def __str__(self) -> str:
        if self.is_empty():
            return EMPTY_PILE_STR
        return str(self.peek_top_card())

class FoundationPile(Pile):
    def __init__(self):
        super().__init__()
        self.suit_allowed: Optional[Suit] = None

    def can_add_card(self, card: Card) -> bool:
        if not card.face_up:
            return False
        if self.is_empty():
            if card.rank == Rank.ACE:
                return True
            return False
        else:
            top_card = self.peek_top_card()
            if top_card:
                return (card.suit == self.suit_allowed and 
                        card.rank.value == top_card.rank.value + 1)
            return False 

    def add_card(self, card: Card) -> None:
        super().add_card(card)
        if len(self.cards) == 1 and card.rank == Rank.ACE:
            self.suit_allowed = card.suit

    def __str__(self) -> str:
        if self.is_empty():
            return f"{EMPTY_PILE_STR}"
        return str(self.peek_top_card())

class TableauPile(Pile):
    def can_add_cards(self, cards_to_add: Union[Card, List[Card]]) -> bool:
        if not isinstance(cards_to_add, list):
            cards_to_add = [cards_to_add]
        
        if not cards_to_add or not cards_to_add[0].face_up:
            return False 

        first_card_to_add = cards_to_add[0]

        if self.is_empty():
            return first_card_to_add.rank == Rank.KING
        else:
            top_pile_card = self.peek_top_card()
            if not top_pile_card or not top_pile_card.face_up:
                return False 
            
            return (first_card_to_add.color != top_pile_card.color and 
                    first_card_to_add.rank.value == top_pile_card.rank.value - 1)

    def flip_top_card_if_needed(self) -> bool:
        """Flips the top card if it's face-down. Returns True if a flip occurred."""
        top_card = self.peek_top_card()
        if top_card and not top_card.face_up:
            top_card.flip()
            return True
        return False

    def get_face_up_cards(self) -> List[Card]:
        """Returns the list of face-up cards from the top of the pile."""
        face_up_stack = []
        for card in reversed(self.cards):
            if card.face_up:
                face_up_stack.insert(0, card) 
            else:
                break 
        return face_up_stack

    def __str__(self) -> str:
        if self.is_empty():
            return EMPTY_PILE_STR
        return ' '.join(str(c) for c in self.cards)