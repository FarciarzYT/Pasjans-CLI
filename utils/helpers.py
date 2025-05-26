import os
import platform
import re 

def clear_console():
    """Czyści ekran konsoli niezależnie od systemu operacyjnego."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def get_visible_length(s: str) -> int:
    """Oblicza widoczną długość stringu po usunięciu kodów ANSI."""
    ansi_escape_pattern = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]') # Wzorzec Regex do znajdowania sekwencji escape ANSI
    return len(ansi_escape_pattern.sub('', s))
