import random
from typing import List, Dict, Any, Optional, Tuple
from .card import Card
from .deck import Deck
from .pile import StockPile, WastePile, FoundationPile, TableauPile
from utils.constants import (
    NUM_TABLEAU_PILES, NUM_FOUNDATION_PILES, DIFFICULTY_EASY, DIFFICULTY_HARD,
    Rank, Suit, MAX_UNDO_MOVES, PILE_STOCK, PILE_WASTE, PILE_FOUNDATION, PILE_TABLEAU
)
from utils.game_settings import get_default_settings as get_default_game_settings


class GameState:
    def __init__(self, difficulty: str = DIFFICULTY_EASY, settings: Optional[Dict[str, Any]] = None):
        self.difficulty = difficulty
        self.current_settings = settings if settings is not None else get_default_game_settings()
        
        self.deck = Deck()
        self.stock_pile = StockPile()
        self.waste_pile = WastePile()
        self.foundation_piles: List[FoundationPile] = []
        self.tableau_piles: List[TableauPile] = []
        self.moves_count = 0
        self.move_history: List[Dict[str, Any]] = []
        self.elapsed_time: float = 0.0 
        self.last_action_was_reshuffle: bool = False 
        self.setup_game()

    def setup_game(self):
        self.deck = Deck()
        self.stock_pile = StockPile()
        self.waste_pile = WastePile()
        self.foundation_piles = [FoundationPile() for _ in range(NUM_FOUNDATION_PILES)]
        self.tableau_piles = [TableauPile() for _ in range(NUM_TABLEAU_PILES)]
        self.moves_count = 0
        self.move_history = []
        self.elapsed_time = 0
        self.last_action_was_reshuffle = False

        for i in range(NUM_TABLEAU_PILES):
            for j in range(i + 1):
                card = self.deck.deal()
                if card:
                    if j == i: card.face_up = True
                    self.tableau_piles[i].add_card(card)
        while not self.deck.is_empty():
            card = self.deck.deal()
            if card:
                card.face_up = False
                self.stock_pile.add_card(card)


    def deal_from_stock(self) -> bool:
        self.last_action_was_reshuffle = False 
        action_details = {'type': 'draw', 'cards_drawn_data': [], 'from': 'stock', 'reshuffled_waste_data': None}
        cards_moved_to_waste_actual_objects = []

        if not self.stock_pile.is_empty():
            num_to_draw = 3 if self.difficulty == DIFFICULTY_HARD else 1
            for _ in range(num_to_draw):
                if self.stock_pile.is_empty(): break
                card = self.stock_pile.remove_top_card()
                if card:
                    card.face_up = True
                    self.waste_pile.add_card(card)
                    cards_moved_to_waste_actual_objects.append(card)
            
            if cards_moved_to_waste_actual_objects:
                action_details['cards_drawn_data'] = [c.__dict__ for c in cards_moved_to_waste_actual_objects]
                self._record_action(action_details)
                self.moves_count += 1
                return True
            return False 
        
        elif self.current_settings.get("reshuffle_waste_on_empty_stock", True) and not self.waste_pile.is_empty():
            action_details['type'] = 'reshuffle_stock'
            action_details['reshuffled_waste_data'] = [c.__dict__ for c in self.waste_pile.cards] 
            
            original_waste_cards = self.waste_pile.get_all_cards_and_clear()
            random.shuffle(original_waste_cards) 
            for card_obj in original_waste_cards: 
                card_obj.face_up = False 
                self.stock_pile.add_card(card_obj)
            
            self._record_action(action_details)
            self.moves_count += 1 
            self.last_action_was_reshuffle = True 
            return True 
        
        
        return False

    def _get_pile_by_id(self, pile_type: str, index: Optional[int] = None):
      
        if pile_type == PILE_STOCK: return self.stock_pile
        if pile_type == PILE_WASTE: return self.waste_pile
        if pile_type == PILE_FOUNDATION and index is not None and 0 <= index < NUM_FOUNDATION_PILES: return self.foundation_piles[index]
        if pile_type == PILE_TABLEAU and index is not None and 0 <= index < NUM_TABLEAU_PILES: return self.tableau_piles[index]
        raise ValueError(f"Invalid pile id: {pile_type}{index+1 if index is not None else ''}")

    def move_cards(self, from_pile_type: str, from_idx: Optional[int],
                   to_pile_type: str, to_idx: Optional[int], num_cards_to_request: int = 1) -> Tuple[bool, str]:
        """
        Przenosi karty między stosami.
        Zwraca (True, "Ruch wykonany.") lub (False, "Opis błędu").
        """
        try:
            source_pile = self._get_pile_by_id(from_pile_type, from_idx)
            dest_pile = self._get_pile_by_id(to_pile_type, to_idx)
        except ValueError as e:
            return False, str(e)

        # Pobierz karty do przeniesienia
        cards_to_move_actual_objects: List[Card] = self._get_cards_to_move(source_pile, num_cards_to_request)
        if isinstance(cards_to_move_actual_objects, str):
            # Zwrócony string to komunikat o błędzie
            return False, cards_to_move_actual_objects
        if not cards_to_move_actual_objects:
            return False, "Brak kart do przeniesienia."

        # Sprawdź, czy ruch jest dozwolony
        can_move, error_msg = self._can_move_to_dest(dest_pile, cards_to_move_actual_objects)
        if not can_move:
            return False, error_msg

        # Wykonaj ruch
        action = {
            'type': 'move',
            'from_pile_type': from_pile_type,
            'from_idx': from_idx,
            'to_pile_type': to_pile_type,
            'to_idx': to_idx,
            'moved_cards_data': [c.__dict__ for c in cards_to_move_actual_objects],
            'source_top_card_flipped_this_move': False
        }

        self._remove_cards_from_source(source_pile, cards_to_move_actual_objects)
        if isinstance(source_pile, TableauPile) and source_pile.flip_top_card_if_needed():
            action['source_top_card_flipped_this_move'] = True
        dest_pile.add_cards(cards_to_move_actual_objects)
        if isinstance(dest_pile, FoundationPile) and len(dest_pile.cards) == 1 and cards_to_move_actual_objects[0].rank == Rank.ACE:
            dest_pile.suit_allowed = cards_to_move_actual_objects[0].suit
        self._record_action(action)
        self.moves_count += 1
        return True, "Ruch wykonany."

    def _get_cards_to_move(self, source_pile, num_cards_to_request: int):
        """
        Zwraca listę kart do przeniesienia lub komunikat o błędzie (str).
        """
        if source_pile == self.waste_pile:
            if num_cards_to_request != 1:
                return "Tylko 1 karta z Waste."
            card = self.waste_pile.get_playable_card()
            return [card] if card else []
        elif isinstance(source_pile, TableauPile):
            if num_cards_to_request < 1:
                return "Liczba kart > 0."
            potential_stack = source_pile.peek_cards_from_top(num_cards_to_request)
            if len(potential_stack) == num_cards_to_request and all(c.face_up for c in potential_stack):
                return potential_stack
            else:
                return "Nie można przenieść (za mało/nieodkryte)."
        elif isinstance(source_pile, FoundationPile):
            if num_cards_to_request != 1:
                return "Tylko 1 karta z Fundamentu."
            card = source_pile.peek_top_card()
            return [card] if card else []
        else:
            return "Nieprawidłowy stos źródłowy."

    def _can_move_to_dest(self, dest_pile, cards_to_move_actual_objects: List[Card]) -> Tuple[bool, str]:
        """
        Sprawdza, czy można przenieść karty na docelowy stos.
        Zwraca (True, "") lub (False, "Opis błędu").
        """
        if isinstance(dest_pile, FoundationPile):
            if len(cards_to_move_actual_objects) == 1 and dest_pile.can_add_card(cards_to_move_actual_objects[0]):
                return True, ""
            else:
                return False, "Nieprawidłowy ruch do celu."
        elif isinstance(dest_pile, TableauPile):
            if dest_pile.can_add_cards(cards_to_move_actual_objects):
                return True, ""
            else:
                return False, "Nieprawidłowy ruch do celu."
        else:
            return False, "Nieprawidłowy stos docelowy."

    def _remove_cards_from_source(self, source_pile, cards_to_move_actual_objects: List[Card]):
        """
        Usuwa karty ze źródłowego stosu.
        """
        if source_pile == self.waste_pile:
            source_pile.remove_top_card()
        elif isinstance(source_pile, (TableauPile, FoundationPile)):
            source_pile.remove_cards_from_top(len(cards_to_move_actual_objects))

    def _record_action(self, action_details: Dict[str, Any]):
        
        self.move_history.append(action_details)
        if len(self.move_history) > MAX_UNDO_MOVES: self.move_history.pop(0)

    def _recreate_card_from_data(self, card_data: Dict[str, Any]) -> Card:
      
        suit_enum_instance = card_data['suit']; rank_enum_instance = card_data['rank']
        actual_suit = Suit[suit_enum_instance.name]; actual_rank = Rank[rank_enum_instance.name]
        return Card(actual_suit, actual_rank, card_data['face_up'])

    def undo_last_move(self) -> bool:
        """
        Cofa ostatni ruch gracza. Zwraca True jeśli cofnięcie się powiodło, False w przeciwnym wypadku.
        """
        if not self.move_history:
            return False
        last_action = self.move_history.pop()
        action_type = last_action['type']

        if action_type == 'draw':
            self._undo_draw_action(last_action)
        elif action_type == 'reshuffle_stock':
            self._undo_reshuffle_action(last_action)
        elif action_type == 'move':
            self._undo_move_action(last_action)
        else:
            return False

        self.moves_count = max(0, self.moves_count - 1)
        return True

    def _undo_draw_action(self, last_action: Dict[str, Any]):
        """Cofa akcję dobierania kart ze stocka."""
        cards_drawn_data = last_action['cards_drawn_data']
        for _ in range(len(cards_drawn_data)):
            self.waste_pile.remove_top_card()
        for card_data_dict in reversed(cards_drawn_data):
            self.stock_pile.add_card(self._recreate_card_from_data(card_data_dict))

    def _undo_reshuffle_action(self, last_action: Dict[str, Any]):
        """Cofa akcję przetasowania stosu odpadów do stocka."""
        self.stock_pile.get_all_cards_and_clear()
        reshuffled_waste_data_list = last_action['reshuffled_waste_data']
        if reshuffled_waste_data_list:
            for card_data_dict in reshuffled_waste_data_list:
                self.waste_pile.add_card(self._recreate_card_from_data(card_data_dict))

    def _undo_move_action(self, last_action: Dict[str, Any]):
        """Cofa akcję przeniesienia kart między stosami."""
        from_pile_type, from_idx = last_action['from_pile_type'], last_action['from_idx']
        to_pile_type, to_idx = last_action['to_pile_type'], last_action['to_idx']
        moved_cards_data_list = last_action['moved_cards_data']
        source_card_was_flipped = last_action['source_top_card_flipped_this_move']
        source_pile = self._get_pile_by_id(from_pile_type, from_idx)
        dest_pile = self._get_pile_by_id(to_pile_type, to_idx)
        cards_to_restore = [self._recreate_card_from_data(cd) for cd in moved_cards_data_list]
        dest_pile.remove_cards_from_top(len(cards_to_restore))
        if isinstance(dest_pile, FoundationPile) and dest_pile.is_empty():
            dest_pile.suit_allowed = None
        if isinstance(source_pile, TableauPile) and source_card_was_flipped:
            top_card = source_pile.peek_top_card()
            if top_card and top_card.face_up:
                top_card.face_up = False
        source_pile.add_cards(cards_to_restore)

    def check_win_condition(self) -> bool:
        return sum(len(p) for p in self.foundation_piles) == 52

    def can_move_card_to_pile(self, card_to_move: Card, dest_pile) -> bool:
        if not card_to_move or not card_to_move.face_up: return False
        if isinstance(dest_pile, FoundationPile): return dest_pile.can_add_card(card_to_move)
        elif isinstance(dest_pile, TableauPile): return dest_pile.can_add_cards([card_to_move])
        return False

    def can_move_stack_to_tableau(self, stack_to_move: List[Card], dest_tableau_pile: TableauPile) -> bool:
        if not stack_to_move: return False
        return dest_tableau_pile.can_add_cards(stack_to_move)

    def has_possible_moves(self) -> bool:
        """
        Sprawdza, czy gracz ma jakiekolwiek możliwe ruchy do wykonania.
        """
        if not self.stock_pile.is_empty():
            return True
        # Jeśli stock jest pusty, ale można przetasować waste, to też jest "ruch" (draw spowoduje reshuffle)
        if self.stock_pile.is_empty() and \
           self.current_settings.get("reshuffle_waste_on_empty_stock", True) and \
           not self.waste_pile.is_empty():
            return True

        if self._waste_has_possible_moves():
            return True
        if self._tableau_has_possible_moves():
            return True
        return False

    def _waste_has_possible_moves(self) -> bool:
        """Sprawdza, czy karta z waste może być zagrana na foundation lub tableau."""
        waste_card = self.waste_pile.get_playable_card()
        if waste_card:
            for f_pile in self.foundation_piles:
                if self.can_move_card_to_pile(waste_card, f_pile):
                    return True
            for t_pile in self.tableau_piles:
                if self.can_move_card_to_pile(waste_card, t_pile):
                    return True
        return False

    def _tableau_has_possible_moves(self) -> bool:
        """Sprawdza, czy na tableau są możliwe ruchy (na foundation lub inne tableau)."""
        for i, t_pile_src in enumerate(self.tableau_piles):
            if not t_pile_src.is_empty():
                top_tableau_card = t_pile_src.peek_top_card()
                if top_tableau_card and top_tableau_card.face_up:
                    for f_pile_dest in self.foundation_piles:
                        if self.can_move_card_to_pile(top_tableau_card, f_pile_dest):
                            return True
            face_up_stack_on_src = t_pile_src.get_face_up_cards()
            if not face_up_stack_on_src:
                continue
            for k in range(len(face_up_stack_on_src)):
                stack_to_check = face_up_stack_on_src[k:]
                if not stack_to_check:
                    continue
                for j, t_pile_dest in enumerate(self.tableau_piles):
                    if i == j:
                        continue
                    if self.can_move_stack_to_tableau(stack_to_check, t_pile_dest):
                        return True
        return False
    