"""
decision.py
Implements the decision function f(s, a) based on Information Gain (Shannon entropy).

    a* = argmax f(s, a)

f(s, a) = Shannon entropy of the pattern distribution when guessing `a`
          against all remaining candidates in V.

No speed shortcuts — scoring all probe words every turn is the correct
approach for a ~12k vocabulary. At ~2s/turn this is perfectly acceptable.
"""

import math
from collections import Counter

from state import AgentState, get_pattern

FIRST_GUESS = "crane"


def pattern_entropy(guess: str, candidates: list[str]) -> float:
    """Expected entropy of guessing `guess` given the current candidates."""
    if not candidates:
        return 0.0
    counts: Counter = Counter(
        tuple(get_pattern(guess, answer)) for answer in candidates
    )
    total = len(candidates)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def choose_best_guess(state: AgentState, probe_words: list[str]) -> str:
    """
    Score every word in probe_words against the current candidates and
    return the one that maximises expected entropy.
    A small bonus (+0.1) is applied to words that are themselves candidates,
    so that equally-informative guesses that could win immediately are preferred.
    """
    candidates = state.vocabulary

    if len(candidates) <= 2:
        return candidates[0]

    best_word = None
    best_score = -1.0
    candidate_set = set(candidates)

    for word in probe_words:
        score = pattern_entropy(word, candidates)
        if word in candidate_set:
            score += 0.1
        if score > best_score:
            best_score = score
            best_word = word

    return best_word  # type: ignore[return-value]


def choose_action(state: AgentState, probe_words: list[str]) -> str:
    """Given a state, return the best word to guess next."""
    if state.attempt_number == 0 and FIRST_GUESS in probe_words:
        return FIRST_GUESS
    return choose_best_guess(state, probe_words)
