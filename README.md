# Gra Pasjans w Pythonie

Konsolowa implementacja klasycznej gry karcianej Pasjans (Klondike), stworzona jako projekt na konkurs programistyczny Gigathon. Gra oferuje różne opcje personalizacji, śledzenie najlepszych wyników oraz różne poziomy trudności.

## 1. Jak Uruchomić Projekt

1.  **Wymagania Wstępne:**
    *   Zainstalowany Python w wersji 3.7 lub nowszej.
    *   `pip` (instalator pakietów Pythona).

2.  **Instalacja:**
    *   Sklonuj lub pobierz repozytorium/pliki projektu.
    *   Przejdź do katalogu `Pasjans` w terminalu.
    *   Zainstaluj wymagane zależności (obecnie `colorama` do kolorowego tekstu):
        ```bash
        pip install -r requirements.txt
        ```

3.  **Uruchamianie Gry:**
    *   Będąc w katalogu `Pasjans`, uruchom:
        ```bash
        python main.py
        ```
    *   Spowoduje to uruchomienie menu głównego gry.

## 2. Funkcje Gry

*   **Klasyczna Rozgrywka Pasjansa Klondike:** Standardowe zasady dla stosów roboczych, fundamentowych, talii rezerwowej i stosu odkrytych.
*   **Menu Główne:** Łatwa nawigacja do rozpoczęcia nowej gry, zmiany ustawień, przeglądania najlepszych wyników, czytania zasad lub wyjścia z gry.
*   **Personalizowane Ustawienia (zapisywane w `settings.json`):**
    *   **Poziom Trudności:**
        *   `Łatwy`: Ciągnie 1 kartę z Talii Rezerwowej.
        *   `Trudny`: Ciągnie 3 karty z Talii Rezerwowej (tylko wierzchnia karta ze Stosu Odkrytych jest grywalna).
    *   **Styl Wyświetlania Kart:**
        *   `Minimalistyczny (A♠)`: Prosta reprezentacja tekstowa (np. `A♠`, `K♥`).
        *   `ASCII ([A♠])`: Podobny do minimalistycznego, ale karty są w nawiasach `[]` (np. `[A♠]`, `[K♥]`).
        *   `Emoji (🂡)`: Używa symboli Unicode dla kart (wymaga wsparcia terminala i czcionki).
    *   **Motyw Kolorystyczny:**
        *   `Ciemny`: Jasny tekst/karty na ciemnym (domyślnym terminala) tle.
        *   `Jasny`: Ciemny tekst/karty na jasnym tle (najlepiej, jeśli tło terminala jest jasne).
    *   **Licznik Czasu Gry:** Opcja włączenia lub wyłączenia licznika czasu w grze.
    *   **Cofanie Ruchów:** Opcja włączenia lub wyłączenia możliwości cofania ruchów (do 3 ruchów).
    *   **Przetasowywanie Talii:** Opcja wyboru:
        *   Przetasowanie kart ze Stosu Odkrytych z powrotem do Talii Rezerwowej, gdy ta jest pusta (klasyczne zachowanie).
        *   Zakończenie gry porażką, jeśli Talia Rezerwowa jest pusta i nie ma więcej możliwych ruchów (bardziej wymagające).
*   **Śledzenie Najlepszych Wyników:** Zapisuje liczbę ruchów dla wygranych gier w pliku `solitaire_high_scores.txt`.
*   **Interfejs Konsolowy:** W pełni grywalna w standardowym terminalu, z użyciem kolorów dla lepszej widoczności kart.

## 3. Instrukcja Gry (Sterowanie)

Gra jest kontrolowana poprzez wpisywanie komend w konsoli.

### Nawigacja w Menu Głównym:
*   Wpisz numer odpowiadający wybranej opcji (np. `1` dla "Nowa Gra").

### Komendy w Trakcie Gry:
*   **`draw` (lub `d`)**: Ciągnie kartę(y) z Talii Rezerwowej (Stock) na Stos Odkrytych (Waste). Liczba ciągniętych kart zależy od ustawionego poziomu trudności. Jeśli Talia Rezerwowa jest pusta, a opcja "Przetasowywanie" jest włączona, ta komenda przeniesie karty ze Stosu Odkrytych z powrotem do Talii i je przetasuje.
*   **`move <źródło> <cel> [liczba_kart]` (lub `m <źr> <cel> [n]`)**:
    *   Przenosi kartę(y) ze stosu źródłowego na stos docelowy.
    *   `<źródło>` i `<cel>` mogą być:
        *   `W` (Stos Odkrytych - zawsze pobierana jest wierzchnia grywalna karta).
        *   `F<n>` (Stos Fundamentowy <n>, np. `F1`, `F2`, `F3`, `F4`).
        *   `T<n>` (Stos Roboczy <n>, np. `T1`, `T2`, ..., `T7`).
    *   `[liczba_kart]` (opcjonalnie, domyślnie 1): Określa liczbę kart do przeniesienia ze Stosu Roboczego (jako sekwencja). Ze Stosu Odkrytych i Fundamentowego można przenieść tylko 1 kartę na raz.
    *   Przykłady:
        *   `m W T1` (Przenieś wierzchnią kartę z Waste na Tableau 1)
        *   `m T2 F1` (Przenieś wierzchnią kartę z Tableau 2 na Fundament 1)
        *   `m T3 T5 3` (Przenieś 3 wierzchnie odkryte karty z Tableau 3 na Tableau 5)
*   **`undo` (lub `u`)**: Cofa ostatni ruch, jeśli opcja "Cofanie Ruchów" jest włączona (można cofnąć do 3 ruchów).
*   **`new` (lub `n`)**: Restartuje bieżącą sesję gry z tymi samymi ustawieniami, po potwierdzeniu.
*   **`menu`**: Wraca do menu głównego, kończąc bieżącą sesję gry po potwierdzeniu.
*   **`quit` (lub `q`)**: Całkowicie zamyka program Pasjans po potwierdzeniu.
*   **`help` (lub `h`)**: Wyświetla listę dostępnych komend w grze.

### Menu Ustawień:
*   Wpisz numer odpowiadający ustawieniu, które chcesz zmienić.
*   Postępuj zgodnie z instrukcjami na ekranie, aby wybrać nowe wartości.
*   Wpisz `s`, aby zapisać zmiany i wrócić do menu głównego.
*   Wpisz `x`, aby anulować zmiany i wrócić do menu głównego.

**Cel Gry:**
Przenieść wszystkie 52 karty na cztery Stosy Fundamentowe, ułożone według koloru kart (kier, karo, pik, trefl) od Asa (A) do Króla (K).

**Wygrana:**
Gra jest wygrana, gdy wszystkie karty zostaną poprawnie umieszczone na Stosach Fundamentowych. Wyświetlony zostanie komunikat o wygranej wraz z liczbą ruchów i czasem gry (jeśli włączony). Twój wynik (liczba ruchów) zostanie zapisany.

**Przegrana:**
Gra jest przegrana, jeśli Talia Rezerwowa jest pusta (a opcja przetasowywania jest wyłączona lub Stos Odkrytych również jest pusty) i nie ma już żadnych możliwych legalnych ruchów na planszy. Wyświetlony zostanie komunikat o zakończeniu gry.

## 4. Struktura Projektu
```
Pasjans/
├── main.py # Główny skrypt aplikacji, pętla menu, pętla gry
├── game_logic/
│ ├── init.py
│ ├── card.py # Klasa Card (kolor, figura, wartość, czy odkryta)
│ ├── deck.py # Klasa Deck (talia kart, tasowanie)
│ ├── pile.py # Bazowa klasa Pile i wyspecjalizowane typy stosów
│ └── game_state.py # Zarządza elementami gry, zasadami, ruchami, cofaniem, wygraną/przegraną
├── ui/
│ ├── init.py
│ ├── console_ui.py # Obsługuje interakcję z użytkownikiem w konsoli, wyświetlanie planszy i menu
├── utils/
│ ├── init.py
│ ├── constants.py # Stałe gry (figury, kolory kart, identyfikatory stosów)
│ ├── game_settings.py # Zarządza wczytywaniem i zapisywaniem ustawień gry z/do JSON
│ ├── helpers.py # Funkcje pomocnicze (np. czyszczenie konsoli, obliczanie widocznej długości tekstu)
│ └── high_score.py # Zarządza najlepszymi wynikami (odczyt/zapis do pliku)
├── README.md # Ten plik
├── requirements.txt # Zależności Python (np. colorama)
└── settings.json # Przechowuje konfigurowalne przez użytkownika ustawienia gry
└── solitaire_high_scores.txt # Przechowuje najlepsze wyniki (tworzony automatycznie)
```
## 5. Opis Kluczowych Klas, Modułów i Funkcji

### `main.py`
*   Zawiera główny punkt wejścia aplikacji (`main_menu_loop`).
*   Zarządza nawigacją w menu głównym.
*   Uruchamia i kontroluje pętlę gry (`run_game_loop`).
*   Obsługuje wprowadzane przez użytkownika komendy gry i deleguje akcje do `GameState` i `ConsoleUI`.
*   Zarządza pętlą menu ustawień (`show_settings_menu`).

### `game_logic/game_state.py`
*   **Klasa `GameState`:**
    *   Rdzeń logiki gry.
    *   Inicjalizuje i zarządza wszystkimi stosami kart (Rezerwowy, Odkrytych, Fundamentowe, Robocze).
    *   Obsługuje rozdawanie kart, ruchy kart zgodnie z zasadami gry.
    *   Implementuje funkcjonalność cofania ruchów.
    *   Sprawdza warunki wygranej i przegranej.
    *   Akceptuje ustawienia gry (np. poziom trudności, opcja przetasowywania) w celu dostosowania swojego zachowania.
    *   `has_possible_moves()`: Określa, czy pozostały jakiekolwiek legalne ruchy.

### `ui/console_ui.py`
*   **Klasa `ConsoleUI`:**
    *   Odpowiada za wszystkie interakcje z użytkownikiem w konsoli.
    *   `display_main_menu()`, `display_settings_menu()`, `display_board()`: Renderuje różne ekrany gry.
    *   `_get_card_display_str()`: Formatuje pojedyncze karty na podstawie aktualnych ustawień stylu i motywu.
    *   `ask_*_setting()`: Metody do pobierania od użytkownika wyborów w menu ustawień.
    *   Używa biblioteki `colorama` do kolorowego wyświetlania tekstu.

### `utils/game_settings.py`
*   `load_settings()`: Wczytuje ustawienia z `settings.json`; używa wartości domyślnych, jeśli plik nie istnieje, jest uszkodzony lub brakuje w nim kluczy.
*   `save_settings()`: Zapisuje bieżące ustawienia do `settings.json`.
*   `get_default_settings()`: Dostarcza słownik domyślnych ustawień gry.
*   Zawiera stałe dla opcji ustawień (np. `CARD_STYLE_MINIMAL`, `SETTING_OPTIONS_BOOLEAN`).

### `utils/constants.py`
*   Definiuje Enumy `Suit` (kolor karty) i `Rank` (figura/wartość karty).
*   Zawiera stałe tekstowe dla identyfikatorów stosów (np. `PILE_STOCK`, `PILE_TABLEAU`) i innych parametrów gry.

### `utils/helpers.py`
*   `clear_console()`: Czyści ekran terminala dla różnych systemów operacyjnych.
*   `get_visible_length()`: Oblicza widoczną długość ciągu znaków, ignorując kody escape ANSI (używane do wyrównywania interfejsu).

### `utils/high_score.py`
*   `load_high_scores()`: Wczytuje wyniki z `solitaire_high_scores.txt`.
*   `save_high_score()`: Dodaje nowy wynik i zapisuje posortowaną listę.
*   `get_formatted_high_scores()`: Zwraca sformatowany tekst do wyświetlania najlepszych wyników.

### Pozostałe pliki `game_logic`:
*   `card.py`: Definiuje klasę `Card`.
*   `deck.py`: Definiuje klasę `Deck` dla standardowej talii 52 kart.
*   `pile.py`: Definiuje bazową klasę `Pile` oraz wyspecjalizowane klasy `StockPile`, `WastePile`, `FoundationPile`, `TableauPile`.

## 6. Uwagi Deweloperskie
*   Styl kart ASCII jest obecnie prostą, jednoliniową reprezentacją (np. `[A♠]`) dla łatwiejszego wyrównywania w konsoli. Pełny, wieloliniowy ASCII art wymagałby znaczących zmian w logice renderowania planszy.
*   Wyświetlanie kart Emoji zależy od wsparcia Unicode przez terminal i używaną czcionkę.
*   Motywy kolorystyczne są podstawowe; można by dodać dalszą personalizację.
---
