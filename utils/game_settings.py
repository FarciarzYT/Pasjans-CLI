import json
import os

SETTINGS_FILE = "settings.json"
CARD_STYLE_ASCII = "ascii"
CARD_STYLE_EMOJI = "emoji"
CARD_STYLE_MINIMAL = "minimal"
THEME_LIGHT = "light"
THEME_DARK = "dark"
DEFAULT_DIFFICULTY = "easy" 

def get_default_settings() -> dict:
    """Zwraca domyślny słownik ustawień."""
    return {
        "difficulty": DEFAULT_DIFFICULTY,
        "card_style": CARD_STYLE_MINIMAL,
        "theme": THEME_DARK,
        "timer_enabled": True,
        "undo_enabled": True,
        "reshuffle_waste_on_empty_stock": True, 
    }

def load_settings() -> dict:
    default_settings = get_default_settings()
    if not os.path.exists(SETTINGS_FILE):
        print(f"Plik ustawień '{SETTINGS_FILE}' nie znaleziony. Używam domyślnych.")
        return default_settings.copy()
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        for key, default_value in default_settings.items():
            if key not in settings:
                print(f"Brakujący klucz '{key}' w ustawieniach. Używam domyślnej wartości: {default_value}")
                settings[key] = default_value
        return settings
    except json.JSONDecodeError:
        print(f"Błąd podczas wczytywania pliku '{SETTINGS_FILE}'. Plik może być uszkodzony. Używam domyślnych.")
        return default_settings.copy()
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas wczytywania ustawień: {e}. Używam domyślnych.")
        return default_settings.copy()

def save_settings(settings_to_save: dict):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings_to_save, f, indent=4)
        print(f"Ustawienia zapisane w '{SETTINGS_FILE}'.")
        return True
    except Exception as e:
        print(f"Błąd podczas zapisywania ustawień do '{SETTINGS_FILE}': {e}")
        return False

SETTING_OPTIONS_DIFFICULTY = {"easy": "Łatwy", "hard": "Trudny"}
SETTING_OPTIONS_CARD_STYLE = {
    CARD_STYLE_ASCII: "ASCII ([A♠])",
    CARD_STYLE_EMOJI: "Emoji (🂡)",
    CARD_STYLE_MINIMAL: "Minimalistyczny (A♠)"
}
SETTING_OPTIONS_THEME = {THEME_LIGHT: "Jasny", THEME_DARK: "Ciemny"}
SETTING_OPTIONS_BOOLEAN = {True: "Włączone", False: "Wyłączone"}

SETTING_OPTIONS_RESHUFFLE = {
    True: "Tak (klasycznie, przetasuj)", 
    False: "Nie (koniec kart = koniec gry, jeśli brak ruchów)"
}