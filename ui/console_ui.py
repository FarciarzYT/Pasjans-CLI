from colorama import Fore, Style, init as colorama_init
from typing import TYPE_CHECKING, List, Optional, Tuple, Dict, Any, Union
from utils.constants import (
    Suit, Rank, PILE_STOCK, PILE_WASTE,
    PILE_FOUNDATION, PILE_TABLEAU, EMPTY_PILE_STR, FACE_DOWN_CARD_STR,
    NUM_FOUNDATION_PILES, NUM_TABLEAU_PILES
)
from utils.game_settings import (
    CARD_STYLE_ASCII, CARD_STYLE_EMOJI, CARD_STYLE_MINIMAL,
    THEME_LIGHT, THEME_DARK,
    SETTING_OPTIONS_DIFFICULTY, 
    SETTING_OPTIONS_CARD_STYLE, 
    SETTING_OPTIONS_THEME, 
    SETTING_OPTIONS_BOOLEAN,
    SETTING_OPTIONS_RESHUFFLE, 
    get_default_settings as get_default_game_settings
)
from utils.helpers import clear_console, get_visible_length

if TYPE_CHECKING:
    from game_logic.game_state import GameState
    from game_logic.card import Card

class ConsoleUI:
    def __init__(self):
        colorama_init(autoreset=True)
        self.current_settings: Dict[str, Any] = get_default_game_settings()

    def update_settings_for_ui(self, settings: Dict[str, Any]):
        self.current_settings = settings.copy()

    def _get_card_colors(self) -> Tuple[str, str, str]:
        theme = self.current_settings.get("theme", THEME_DARK)
        if theme == THEME_LIGHT:
            return Fore.RED, Fore.BLACK, Fore.BLACK
        else:
            return Fore.RED, Fore.WHITE, Fore.WHITE

    def _get_card_display_str(self, 
                              card: Optional['Card'], 
                              target_visible_width: Optional[int] = None, 
                              is_tableau_empty_slot: bool = False,
                              is_other_empty_slot: bool = False
                             ) -> str:
        active_card_style = self.current_settings.get("card_style", CARD_STYLE_MINIMAL)
        base_str = ""

        if is_tableau_empty_slot:
            base_str = "" 
        elif is_other_empty_slot:
            base_str = "---" 
        elif not card or not hasattr(card, 'face_up'):
            if active_card_style == CARD_STYLE_ASCII: base_str = " "
            elif active_card_style == CARD_STYLE_EMOJI: base_str = " "
            else: base_str = " " 
        elif not card.face_up:
            if active_card_style == CARD_STYLE_ASCII: base_str = "[ XX ]"
            elif active_card_style == CARD_STYLE_EMOJI: base_str = "🂠 "
            else: base_str = FACE_DOWN_CARD_STR
        else:
            red_color, black_color, _ = self._get_card_colors()
            card_color_code = red_color if card.color == "RED" else black_color
            rank_symbol = card.rank.symbol
            suit_symbol = card.suit.value

            if active_card_style == CARD_STYLE_ASCII:
                base_str = f"{card_color_code}[{rank_symbol}{suit_symbol}]{Style.RESET_ALL}"
            elif active_card_style == CARD_STYLE_EMOJI:
                suit_map_val = {Suit.SPADES: 0xA0, Suit.HEARTS: 0xB0, Suit.DIAMONDS: 0xC0, Suit.CLUBS: 0xD0}
                rank_val = card.rank.value; offset = 0
                if rank_val == 1: offset = 1
                elif 2 <= rank_val <= 10: offset = rank_val
                elif rank_val == 11: offset = 0x0B
                elif rank_val == 12: offset = 0x0D
                elif rank_val == 13: offset = 0x0E
                else: base_str = f"{card_color_code}{rank_symbol}{suit_symbol}{Style.RESET_ALL} "
                if not base_str:
                    try:
                        if card.suit not in suit_map_val: raise KeyError
                        char_code = 0x1F000 + suit_map_val[card.suit] + offset
                        base_str = f"{chr(char_code)} "
                    except: base_str = f"{card_color_code}{rank_symbol}{suit_symbol}{Style.RESET_ALL} "
            else: 
                base_str = f"{card_color_code}{rank_symbol}{suit_symbol}{Style.RESET_ALL}"
        
        if target_visible_width is not None:
            visible_len = get_visible_length(base_str)
            padding_total = target_visible_width - visible_len
            if padding_total > 0:
                pad_left = padding_total // 2
                pad_right = padding_total - pad_left
                return (" " * pad_left) + base_str + (" " * pad_right)
        return base_str

    def display_board(self, game_state: 'GameState'):
        clear_console()
        _, _, default_text_color = self._get_card_colors()
        print(f"{default_text_color}" + "="*70 + "\n")

        stock_obj = game_state.stock_pile
        waste_obj = game_state.waste_pile
        card_style = self.current_settings.get("card_style", CARD_STYLE_MINIMAL)
        single_card_target_width = 4 
        if card_style == CARD_STYLE_ASCII: single_card_target_width = 6
        elif card_style == CARD_STYLE_EMOJI: single_card_target_width = 2 

        if stock_obj.is_empty():
            stock_display_str = self._get_card_display_str(None, single_card_target_width, is_other_empty_slot=True)
        else:
            stock_base_str = f"[S:{len(stock_obj)}]"
            visible_len_stock_base = get_visible_length(stock_base_str)
            padding_total_stock = single_card_target_width - visible_len_stock_base
            pad_left_stock = padding_total_stock // 2 if padding_total_stock > 0 else 0
            pad_right_stock = padding_total_stock - pad_left_stock if padding_total_stock > 0 else 0
            stock_display_str = (" " * pad_left_stock) + stock_base_str + (" " * pad_right_stock)
            if get_visible_length(stock_display_str) < single_card_target_width :
                stock_display_str += " " * (single_card_target_width - get_visible_length(stock_display_str))

        waste_display_cards = waste_obj.get_display_cards(game_state.difficulty)
        if not waste_display_cards:
            waste_str_display = self._get_card_display_str(None, single_card_target_width, is_other_empty_slot=True)
        else:
            waste_str_parts = [self._get_card_display_str(c, single_card_target_width) for c in waste_display_cards]
            waste_str_display = ' '.join(waste_str_parts)
        
        print(f"{default_text_color}{PILE_STOCK:<3}: {stock_display_str}       {PILE_WASTE:<3}: {waste_str_display}")
        print(f"{default_text_color}" + "-" * 70)

        f_header = "Foundations: "
        f_display_parts = []
        foundation_part_label_width = 3 
        foundation_element_width = foundation_part_label_width + single_card_target_width + 2 

        for i, pile in enumerate(game_state.foundation_piles):
            label = f"{PILE_FOUNDATION}{i+1}:"
            top_card = pile.peek_top_card()
            card_str_formatted = self._get_card_display_str(top_card, single_card_target_width, is_other_empty_slot=(not top_card))
            part_str = label + card_str_formatted
            f_display_parts.append(part_str.ljust(foundation_element_width))

        print(f"{default_text_color}{f_header}" + "".join(f_display_parts))
        print(f"{default_text_color}" + "-" * 70)

        print(f"{default_text_color}Tableaus:")
        tableau_col_visible_width = single_card_target_width
        header_parts = [f"{PILE_TABLEAU}{i+1}".center(tableau_col_visible_width) for i in range(NUM_TABLEAU_PILES)]
        print(f"{default_text_color}  " + "  ".join(header_parts))

        max_cards_in_tableau = 0
        for pile in game_state.tableau_piles:
            if len(pile.cards) > max_cards_in_tableau:
                max_cards_in_tableau = len(pile.cards)
        
        if max_cards_in_tableau == 0:
             empty_tableau_cell = self._get_card_display_str(None, tableau_col_visible_width, is_tableau_empty_slot=True)
             print(f"{default_text_color}  " + "  ".join([empty_tableau_cell] * NUM_TABLEAU_PILES))

        for i in range(max_cards_in_tableau):
            row_cells = []
            for pile_obj in game_state.tableau_piles:
                if i < len(pile_obj.cards):
                    cell_content = self._get_card_display_str(pile_obj.cards[i], tableau_col_visible_width)
                else:
                    cell_content = self._get_card_display_str(None, tableau_col_visible_width, is_tableau_empty_slot=True)
                row_cells.append(cell_content)
            print(f"{default_text_color}  " + "  ".join(row_cells))
        
        print(f"\n{default_text_color}" + "="*70)
        timer_display = ""
        if self.current_settings.get("timer_enabled", True) and hasattr(game_state, 'elapsed_time'):
             minutes = int(game_state.elapsed_time // 60)
             seconds = int(game_state.elapsed_time % 60)
             timer_display = f" | Time: {minutes:02d}:{seconds:02d}"
        print(f"{default_text_color}Moves: {game_state.moves_count} | Difficulty: {game_state.difficulty.capitalize()}{timer_display}")
        print(f"{default_text_color}" + "="*70 + Style.RESET_ALL)

    def display_main_menu(self):
        clear_console()
        _, _, default_text_color = self._get_card_colors()
        print(f"{default_text_color}") 
        print("=" * 30)
        print(f"{Fore.CYAN}{Style.BRIGHT}   PASJANS - MENU GŁÓWNE   {Style.RESET_ALL}")
        print("=" * 30)
        print("1. Nowa Gra")
        print("2. Ustawienia")
        print("3. Najlepsze Wyniki")
        print("4. Zasady Gry")
        print("5. Wyjście")
        print("-" * 30)

    def display_settings_menu(self, current_settings: dict):
        clear_console()
        _, _, default_text_color = self._get_card_colors()
        print(f"{default_text_color}")
        print("=" * 60) 
        print(f"{Fore.CYAN}{Style.BRIGHT}                         USTAWIENIA                         {Style.RESET_ALL}")
        print("=" * 60)
        print(" | Zaleca się korzystać z domyślnych ustawień |")
        print(f"Aktualne ustawienia:")
        print(f"  1. Poziom trudności : {SETTING_OPTIONS_DIFFICULTY.get(current_settings.get('difficulty'), 'N/A')}")
        print(f"  2. Styl kart        : {SETTING_OPTIONS_CARD_STYLE.get(current_settings.get('card_style'), 'N/A')}")
        print(f"  3. Motyw kolorów    : {SETTING_OPTIONS_THEME.get(current_settings.get('theme'), 'N/A')} ")
        print(f"  4. Mierzenie czasu  : {SETTING_OPTIONS_BOOLEAN.get(current_settings.get('timer_enabled', True), 'N/A')}")
        print(f"  5. Cofanie ruchów   : {SETTING_OPTIONS_BOOLEAN.get(current_settings.get('undo_enabled', True), 'N/A')}")
        print(f"  6. Przetasowanie Waste: {SETTING_OPTIONS_RESHUFFLE.get(current_settings.get('reshuffle_waste_on_empty_stock', True), 'N/A')}") 
        print("-" * 60)
        print("Wpisz numer opcji (1-6), aby ją zmienić.")
        print("s. Zapisz i Wróć do Menu Głównego")
        print("x. Anuluj i Wróć do Menu Głównego")
        print("-" * 60)

    def ask_setting_choice(self, prompt: str, options: Dict[Any, str], current_value: Any) -> Any:
        clear_console()
        _, _, default_text_color = self._get_card_colors()
        print(f"{default_text_color}{prompt}")
        
        numbered_options_map: Dict[str, Any] = {}
        idx = 1
        for key_option, display_name in options.items():
            print(f"  [{idx}] {display_name}{' (aktualnie)' if key_option == current_value else ''}")
            numbered_options_map[str(idx)] = key_option
            idx += 1
        print(f"  [x] Anuluj")

        while True:
            choice = input(f"{default_text_color}Twój wybór: {Style.RESET_ALL}").strip().lower()
            if choice == 'x':
                return current_value 
            if choice in numbered_options_map:
                return numbered_options_map[choice]
            self.display_message("Niepoprawny wybór.", is_error=True)


    def ask_difficulty_setting(self, current_difficulty: str) -> str:
        return self.ask_setting_choice(
            "Wybierz nowy poziom trudności:",
            SETTING_OPTIONS_DIFFICULTY,
            current_difficulty
        )

    def ask_card_style_setting(self, current_style: str) -> str:
        return self.ask_setting_choice(
            "Wybierz nowy styl kart:",
            SETTING_OPTIONS_CARD_STYLE,
            current_style
        )

    def ask_theme_setting(self, current_theme: str) -> str:
        return self.ask_setting_choice(
            "Wybierz nowy motyw kolorystyczny:",
            SETTING_OPTIONS_THEME,
            current_theme
        )

    def ask_boolean_setting(self, prompt: str, current_value: bool) -> bool:
        return self.ask_setting_choice(
            prompt,
            SETTING_OPTIONS_BOOLEAN, 
            current_value
        )
    
    def ask_reshuffle_setting(self, current_value: bool) -> bool: 
        return self.ask_setting_choice(
            "Czy przetasować karty ze Stosu Odkrytych (Waste) po wyczerpaniu Talii (Stock)?",
            SETTING_OPTIONS_RESHUFFLE,
            current_value
        )

    def display_message(self, message: str, is_error: bool = False):
        _, _, default_text_color = self._get_card_colors()
        color_prefix = Fore.RED if is_error else Fore.GREEN
        print(f"{color_prefix}{'Błąd:' if is_error else 'Info:'}{Style.RESET_ALL} {default_text_color}{message}{Style.RESET_ALL}")

    def display_win_screen(self, moves: int):
        clear_console()
        _, _, default_text_color = self._get_card_colors()
        print(f"{default_text_color}")
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Gratulacje! Wygrałeś/aś w {moves} ruchach!{Style.RESET_ALL}")

    def display_loss_screen(self):
        clear_console()
        _, _, default_text_color = self._get_card_colors()
        print(f"{default_text_color}")
        print(f"\n{Fore.RED}{Style.BRIGHT}Koniec Gry! Brak możliwych ruchów.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Spróbuj ponownie następnym razem!{Style.RESET_ALL}")

    def display_rules(self):
        clear_console()
        _, _, default_text_color = self._get_card_colors()
        # Pobierz aktualne ustawienie reshuffle, aby wyświetlić poprawną regułę
        reshuffle_enabled = self.current_settings.get("reshuffle_waste_on_empty_stock", True)
        reshuffle_rule_text = "Gdy Talia Rezerwowa (Stock) jest pusta, karty ze Stosu Odkrytych (Waste) są przenoszone z powrotem do Stock, tasowane i można z nich ponownie korzystać." \
            if reshuffle_enabled else \
            "Gdy Talia Rezerwowa (Stock) jest pusta, NIE ma możliwości ponownego użycia kart ze Stosu Odkrytych (Waste)."

        rules_text = f"""{default_text_color}
Zasady Gry Pasjans (Klondike):
Cel: Przenieś wszystkie 52 karty na cztery Stosy Fundamentowe.
Stosy Fundamentowe: Buduj rosnąco według koloru (karty tego samego koloru), od Asa do Króla (np. A♥, 2♥, ..., K♥).
Stosy Robocze (Tableau): Buduj malejąco, naprzemiennymi kolorami (np. czarna Dama na czerwonego Króla).
  - Można przenosić pojedyncze karty lub całe, poprawnie ułożone sekwencje odkrytych kart.
  - Pusty Stos Roboczy może być zapełniony tylko Królem (lub sekwencją zaczynającą się od Króla).
Talia Rezerwowa (Stock) i Stos Odkrytych (Waste): 
  - Użyj komendy 'draw' (lub 'd'), aby odkryć karty na Stos Odkrytych.
  - Poziom Łatwy: Odkrywa 1 kartę. Poziom Trudny: Odkrywa 3 karty (tylko wierzchnia jest grywalna).
  - {reshuffle_rule_text}
Wygrana: Gra jest wygrana, gdy wszystkie karty znajdą się na Stosach Fundamentowych.
Przegrana: Gra jest przegrana, gdy Talia Rezerwowa jest pusta, opcja przetasowania jest wyłączona, i nie ma już żadnych możliwych ruchów.
        {Style.RESET_ALL}"""
        print(rules_text)

    def display_high_scores(self, scores_text: str):
        clear_console()
        _, _, default_text_color = self._get_card_colors()
        print(f"{default_text_color}\n--- Najlepsze Wyniki ---")
        print(scores_text) 
        print("----------------------")
        print(Style.RESET_ALL)

    def get_user_input(self, prompt: str = "Twój ruch: ") -> str:
        _, _, default_text_color = self._get_card_colors()
        return input(f"{default_text_color}{prompt}{Style.RESET_ALL}").strip().lower()

    def parse_command(self, command_str: str) -> Optional[Tuple[str, List[str]]]:
        parts = command_str.split()
        if not parts: return None
        return parts[0], parts[1:]

    def parse_pile_identifier(self, s: str) -> Tuple[Optional[str], Optional[int]]:
        s_upper = s.upper()
        if not s_upper: return None, None
        pile_type_char = s_upper[0]
        index_str = s_upper[1:]
        if pile_type_char == PILE_STOCK: return PILE_STOCK, None
        if pile_type_char == PILE_WASTE: return PILE_WASTE, None
        if pile_type_char not in [PILE_FOUNDATION, PILE_TABLEAU]: return None, None 
        if not index_str.isdigit(): return None, None
        try:
            index = int(index_str) - 1 
            if pile_type_char == PILE_FOUNDATION and not (0 <= index < NUM_FOUNDATION_PILES): return None, None
            if pile_type_char == PILE_TABLEAU and not (0 <= index < NUM_TABLEAU_PILES): return None, None
            return pile_type_char, index
        except ValueError: return None, None
        