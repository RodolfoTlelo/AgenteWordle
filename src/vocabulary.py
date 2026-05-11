"""
vocabulary.py
Loads and manages the word lists from the Wordle dataset.

Supports two dataset formats:

1. wordle.csv  (primary, preferred)
   Columns: word, occurrence, day
   - 'word'       : 5-letter string
   - 'occurrence' : corpus frequency (float)
   - 'day'        : Wordle puzzle day number (non-empty → official answer word)

   This gives us two distinct sets:
     • answer_words  – ~2315 words that can BE the hidden answer (have a 'day')
     • probe_words   – all ~12972 words valid to guess (full vocabulary)

2. 5_letters.csv  (legacy fallback)
   Columns: 1,2,3,4,5  (one letter per column)

The agent uses answer_words as V (candidates) and probe_words as the
search space for information-maximising guesses.
"""

import csv
import os


def load_wordle_csv(filepath: str) -> tuple[list[str], list[str]]:
    """
    Parse wordle.csv.
    Returns (answer_words, probe_words).
    answer_words: words with a day value (official Wordle answers).
    probe_words:  all valid words (full guessing vocabulary).
    """
    answer_words: list[tuple[int, str]] = []
    probe_words:  list[str] = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row["word"].strip().lower()
            if len(word) != 5:
                continue
            probe_words.append(word)
            day_raw = row.get("day", "").strip()
            if day_raw:
                try:
                    answer_words.append((int(float(day_raw)), word))
                except ValueError:
                    pass

    answer_words.sort(key=lambda t: t[0])
    return [w for _, w in answer_words], probe_words


def load_legacy_csv(filepath: str) -> list[str]:
    """Parse 5_letters.csv (columns 1-5). Returns flat word list."""
    words = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            letters = [c.strip() for c in row if c.strip()]
            if len(letters) == 5:
                words.append("".join(letters).lower())
    return words


def _data_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def get_wordle_csv_path() -> str:
    return os.path.join(_data_dir(), "wordle.csv")


def get_legacy_csv_path() -> str:
    return os.path.join(_data_dir(), "5_letters.csv")


def _looks_like_wordle_csv(path: str) -> bool:
    try:
        with open(path, newline="", encoding="utf-8") as f:
            header = f.readline().strip().lower()
        return "word" in header and "occurrence" in header
    except Exception:
        return False


def load_vocabulary(filepath: str | None = None) -> tuple[list[str], list[str]]:
    """
    Load vocabulary. Returns (answer_words, probe_words).
    Priority: wordle.csv > 5_letters.csv.
    For legacy format, answer_words == probe_words.
    """
    path = filepath

    if path is None:
        wordle_path = get_wordle_csv_path()
        legacy_path = get_legacy_csv_path()
        if os.path.exists(wordle_path):
            path = wordle_path
        elif os.path.exists(legacy_path):
            path = legacy_path
        else:
            raise FileNotFoundError(
                "No vocabulary file found. Expected data/wordle.csv or data/5_letters.csv"
            )

    if _looks_like_wordle_csv(path):
        return load_wordle_csv(path)
    else:
        words = load_legacy_csv(path)
        return words, words
