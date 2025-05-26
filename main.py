from game_logic.game_state import GameState
from ui.console_ui import ConsoleUI
from utils import high_score, game_settings
from utils.constants import PILE_STOCK
from utils.helpers import clear_console 
import time
import sys

current_game_settings: dict = {}

def run_game_loop(ui: ConsoleUI, settings: dict):
    global current_game_settings
    difficulty = settings.get("difficulty", game_settings.DEFAULT_DIFFICULTY)
    game_state = GameState(difficulty, settings) 
    timer_enabled = settings.get("timer_enabled", True)
    start_time = time.time() if timer_enabled else 0
    game_state.elapsed_time = 0 
    while True:
        if timer_enabled:
            game_state.elapsed_time = time.time() - start_time
        
        ui.display_board(game_state) 
        if game_state.check_win_condition():
            ui.display_win_screen(game_state.moves_count)
            if timer_enabled:
                final_time = game_state.elapsed_time
                minutes = int(final_time // 60); seconds = int(final_time % 60)
                print(f"Czas gry: {minutes:02d}:{seconds:02d}")
            high_score.save_high_score(game_state.moves_count)
            ui.display_high_scores(high_score.get_formatted_high_scores())
            input("\nNaciśnij Enter, aby wrócić do menu głównego..."); clear_console()
            return

        reshuffle_on = settings.get("reshuffle_waste_on_empty_stock", True)
        can_still_draw_or_reshuffle = not game_state.stock_pile.is_empty() or \
                                      (reshuffle_on and not game_state.waste_pile.is_empty())

        if not can_still_draw_or_reshuffle and not game_state.has_possible_moves():
            ui.display_loss_screen()
            if timer_enabled:
                final_time = game_state.elapsed_time
                minutes = int(final_time // 60); seconds = int(final_time % 60)
                print(f"Czas gry: {minutes:02d}:{seconds:02d}")
            ui.display_high_scores(high_score.get_formatted_high_scores())
            input("\nNaciśnij Enter, aby wrócić do menu głównego..."); clear_console()
            return
        
        raw_input_str = ui.get_user_input(f"({difficulty.capitalize()}) Twój ruch (lub 'h' aby zobaczyć pomoc): ")
        
        if raw_input_str == 'menu':
            clear_console()
            confirm_exit = ui.get_user_input("Czy na pewno chcesz wrócić do menu głównego i zakończyć obecną grę? (tak/nie): ")
            if confirm_exit == 'tak': clear_console(); return 
            else: 
                clear_console() 
                continue 
        
        parsed_command_tuple = ui.parse_command(raw_input_str)
        action_performed_message = None 
        error_message = None

        if not parsed_command_tuple:
            error_message = "Niepoprawny format komendy."
        else:
            command, args = parsed_command_tuple

            if command in ['quit', 'q']:
                clear_console()
                confirm_exit_program = ui.get_user_input("Czy na pewno chcesz zakończyć program? (tak/nie): ")
                if confirm_exit_program == 'tak': 
                    clear_console()
                    ui.display_message("Dziękujemy za grę! Do zobaczenia!")
                    sys.exit()
                else:
                    clear_console() 
                    continue
            
            elif command in ['new', 'n']: 
                clear_console()
                confirm_new = ui.get_user_input("Czy na pewno chcesz zrestartować grę? (tak/nie): ")
                if confirm_new == 'tak':
                    game_state = GameState(difficulty, settings) 
                    start_time = time.time() if timer_enabled else 0 
                    game_state.elapsed_time = 0
                    action_performed_message = "Gra zrestartowana."
                else:
                    clear_console() 
            
            elif command in ['undo', 'u']:
                if settings.get("undo_enabled", True):
                    if game_state.undo_last_move():
                        action_performed_message = "Ostatni ruch cofnięty."
                    else:
                        error_message = "Brak ruchów do cofnięcia lub osiągnięto limit."
                else:
                    error_message = "Cofanie ruchów jest wyłączone w ustawieniach."
            elif command in ['draw', 'd']:
                drew_successfully = game_state.deal_from_stock() 
                if drew_successfully:
                    action_performed_message = "Pociągnięto karty / Przetasowano." if game_state.last_action_was_reshuffle else "Pociągnięto karty."
                    game_state.last_action_was_reshuffle = False 
                else: 
                     error_message = "Brak kart do pociągnięcia. Talia i stos odkrytych są puste lub przetasowanie wyłączone."
            elif command in ['move', 'm']:
                if len(args) < 2 or len(args) > 3:
                    error_message = "Format komendy: m <źródło> <cel> [liczba_kart]"
                else:
                    source_str = args[0]; dest_str = args[1]; num_cards_to_move = 1
                    should_process_move = True
                    if len(args) == 3:
                        try:
                            num_cards_to_move = int(args[2])
                            if num_cards_to_move < 1:
                                error_message = "Liczba kart musi być dodatnia."; should_process_move = False
                        except ValueError:
                            error_message = "Niepoprawna liczba kart."; should_process_move = False
                    if should_process_move:
                        source_pile_type, source_idx = ui.parse_pile_identifier(source_str)
                        dest_pile_type, dest_idx = ui.parse_pile_identifier(dest_str)
                        if source_pile_type is None or dest_pile_type is None:
                            error_message = f"Niepoprawny identyfikator stosu."
                        elif source_pile_type == PILE_STOCK:
                            error_message = "Użyj 'draw'."
                        else:
                            success, message = game_state.move_cards(
                                source_pile_type, source_idx, dest_pile_type, dest_idx, num_cards_to_move
                            )
                            if success: action_performed_message = message
                            else: error_message = message
            elif command in ['help', 'h']:
                clear_console()
                print("\nKomendy dostępne w trakcie gry:")
                print("  draw (d)                     : Pociągnij kartę(y) z Talii Rezerwowej.")
                print("  move (m) <źródło> <cel> [n]  : Przenieś n kart (domyślnie 1).")
                print("                                 <źródło>, <cel>: W (Waste), F1-F4, T1-T7.")
                print("                                 Przykład: m W T1, m T2 F1, m T3 T5 2")
                print("  undo (u)                     : Cofnij ostatni ruch (jeśli włączone).")
                print("  new (n)                      : Rozpocznij nową grę z obecnymi ustawieniami.")
                print("  menu                         : Wróć do menu głównego (kończy obecną grę).")
                print("  quit (q)                     : Kończy działanie programu.")
                print("  help (h)                     : Pokaż tę pomoc.\n")
                input("Naciśnij Enter, aby kontynuować...")
                clear_console()
                continue 
            else:
                error_message = f"Nieznana komenda: '{command}'. Wpisz 'help' lub 'h'."

        # Czyszczenie i wyświetlanie komunikatów po przetworzeniu komendy
        clear_console() 
        if error_message:
            ui.display_message(error_message, is_error=True); input("Naciśnij Enter...") 
        elif action_performed_message:
            pass


def show_settings_menu(ui: ConsoleUI):
    global current_game_settings
    temp_settings = current_game_settings.copy()

    while True:
        ui.display_settings_menu(temp_settings)
        choice = ui.get_user_input("Wybierz opcję (1-6), 's' aby zapisać, 'x' aby anulować: ").strip().lower()
        setting_changed_message = None

        if choice == '1':
            new_val = ui.ask_difficulty_setting(temp_settings.get("difficulty", game_settings.DEFAULT_DIFFICULTY))
            if new_val != temp_settings.get("difficulty"):
                temp_settings["difficulty"] = new_val
                setting_changed_message = f"Poziom: {game_settings.SETTING_OPTIONS_DIFFICULTY[new_val]}."
        elif choice == '2':
            new_val = ui.ask_card_style_setting(temp_settings.get("card_style", game_settings.CARD_STYLE_MINIMAL))
            if new_val != temp_settings.get("card_style"):
                temp_settings["card_style"] = new_val; ui.update_settings_for_ui(temp_settings.copy()) 
                setting_changed_message = f"Styl kart: {game_settings.SETTING_OPTIONS_CARD_STYLE[new_val]}."
        elif choice == '3':
            new_val = ui.ask_theme_setting(temp_settings.get("theme", game_settings.THEME_DARK))
            if new_val != temp_settings.get("theme"):
                temp_settings["theme"] = new_val; ui.update_settings_for_ui(temp_settings.copy()) 
                setting_changed_message = f"Motyw: {game_settings.SETTING_OPTIONS_THEME[new_val]}."
        elif choice == '4':
            new_val = ui.ask_boolean_setting("Mierzyć czas rozgrywki?", temp_settings.get("timer_enabled", True))
            if new_val != temp_settings.get("timer_enabled"):
                temp_settings["timer_enabled"] = new_val
                setting_changed_message = f"Mierzenie czasu: {game_settings.SETTING_OPTIONS_BOOLEAN[new_val]}."
        elif choice == '5':
            new_val = ui.ask_boolean_setting("Pozwolić na cofanie ruchów?", temp_settings.get("undo_enabled", True))
            if new_val != temp_settings.get("undo_enabled"):
                temp_settings["undo_enabled"] = new_val
                setting_changed_message = f"Cofanie ruchów: {game_settings.SETTING_OPTIONS_BOOLEAN[new_val]}."
        elif choice == '6': 
            new_val = ui.ask_reshuffle_setting(temp_settings.get("reshuffle_waste_on_empty_stock", True))
            if new_val != temp_settings.get("reshuffle_waste_on_empty_stock"):
                temp_settings["reshuffle_waste_on_empty_stock"] = new_val
                setting_changed_message = f"Przetasowanie Waste: {game_settings.SETTING_OPTIONS_RESHUFFLE[new_val]}."
        elif choice == 's':
            clear_console()
            if game_settings.save_settings(temp_settings):
                current_game_settings = temp_settings.copy()
                ui.update_settings_for_ui(current_game_settings.copy())
                ui.display_message("Ustawienia zapisane.")
            else:
                ui.display_message("Nie udało się zapisać ustawień.", is_error=True)
            input("Naciśnij Enter, aby wrócić do menu głównego..."); clear_console()
            return
        elif choice == 'x':
            clear_console()
            ui.update_settings_for_ui(current_game_settings.copy()) 
            ui.display_message("Zmiany w ustawieniach anulowane.")
            input("Naciśnij Enter, aby wrócić do menu głównego..."); clear_console()
            return
        else:
            ui.display_message("Niepoprawna opcja.", is_error=True)
            input("Naciśnij Enter..."); 
            continue 

        clear_console() 
        if setting_changed_message:
            ui.display_message(setting_changed_message + " (Niezapisane)")
        elif choice in ['1','2','3','4','5','6']: 
            ui.display_message("Brak zmian w tym ustawieniu.")
        input("Naciśnij Enter..."); 

def main_menu_loop():
    global current_game_settings
    current_game_settings = game_settings.load_settings()
    ui = ConsoleUI()
    ui.update_settings_for_ui(current_game_settings.copy())

    while True:
        ui.display_main_menu() 
        choice = ui.get_user_input("Wybierz opcję: ").strip()

        if choice == '1':
            run_game_loop(ui, current_game_settings)
        elif choice == '2':
            show_settings_menu(ui)
        elif choice == '3': 
            clear_console()
            ui.display_high_scores(high_score.get_formatted_high_scores())
            input("\nNaciśnij Enter, aby wrócić do menu..."); clear_console()
        elif choice == '4': 
            clear_console()
            ui.display_rules()
            input("\nNaciśnij Enter, aby wrócić do menu..."); clear_console()
        elif choice == '5': 
            clear_console()
            ui.display_message("Dziękujemy za grę! Do zobaczenia!")
            sys.exit() 
        else:
            clear_console()
            ui.display_message("Niepoprawna opcja, spróbuj ponownie.", is_error=True)
            input("Naciśnij Enter, aby kontynuować...");
           

if __name__ == "__main__":
    main_menu_loop()