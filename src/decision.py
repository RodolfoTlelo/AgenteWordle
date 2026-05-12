import math
from collections import Counter

from state import AgentState, get_pattern

FIRST_GUESS = "crane"


def pattern_entropy(guess: str, candidates: list[str]) -> float:
    if not candidates:
        return 0.0
    counts: Counter = Counter(
        tuple(get_pattern(guess, answer)) for answer in candidates
    )
    total = len(candidates)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def choose_best_guess(state: AgentState, probe_words: list[str]) -> str:

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
    if state.attempt_number == 0 and FIRST_GUESS in probe_words:
        return FIRST_GUESS
    return choose_best_guess(state, probe_words)
