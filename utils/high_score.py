import os

HIGH_SCORE_FILE = "solitaire_high_scores.txt"
MAX_SCORES_DISPLAYED = 10 

def load_high_scores() -> list[int]:
    if not os.path.exists(HIGH_SCORE_FILE):
        return []
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            scores = [int(line.strip()) for line in f if line.strip().isdigit()]
        return sorted(scores) 
    except Exception:
        return []

def save_high_score(moves: int):
    """Dodaje nowy wynik i zapisuje najlepsze wyniki do pliku."""
    scores = load_high_scores()
    scores.append(moves)
    scores = sorted(scores)[:MAX_SCORES_DISPLAYED]
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            for score in scores:
                f.write(f"{score}\n")
    except Exception as e:
        print(f"Warning: Could not save high score: {e}")

def get_formatted_high_scores() -> str:
    scores = load_high_scores()
    if not scores:
        return "No high scores yet."
    
    lines = ["Najlepsze Wyniki:"]
    for i, score in enumerate(scores[:MAX_SCORES_DISPLAYED], 1):
        lines.append(f"{i}. {score} moves")
    return "\n".join(lines)
