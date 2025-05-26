import os
import platform
import re 

def clear_console():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def get_visible_length(s: str) -> int:
    """Oblicza widoczną długość stringu po usunięciu kodów ANSI."""
    # Wzorzec Regex do znajdowania sekwencji escape ANSI
    ansi_escape_pattern = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return len(ansi_escape_pattern.sub('', s))