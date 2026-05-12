from dataclasses import dataclass, field
from typing import Optional

Color = str  # 'green' | 'yellow' | 'gray'
Pattern = list[Color]


@dataclass
class AgentState:
    vocabulary: list[str]                          # V – remaining candidates
    history: list[tuple[str, Pattern]] = field(default_factory=list)  # H

    @property
    def attempt_number(self) -> int:
        return len(self.history)

    @property
    def solved(self) -> bool:
        return bool(self.history and all(c == "green" for c in self.history[-1][1]))

    @property
    def candidates_left(self) -> int:
        return len(self.vocabulary)

    def summary(self) -> str:
        lines = [f"Attempt: {self.attempt_number}/6 | Candidates: {self.candidates_left}"]
        for word, pattern in self.history:
            colored = " ".join(
                f"[{c[0].upper()}]{l}" for l, c in zip(word, pattern)
            )
            lines.append(f"  {word.upper()}  →  {colored}")
        return "\n".join(lines)


def get_pattern(guess: str, answer: str) -> Pattern:
    guess = guess.lower()
    answer = answer.lower()
    pattern: Pattern = ["gray"] * 5

    # First pass: greens
    answer_remaining = list(answer)
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            pattern[i] = "green"
            answer_remaining[i] = None  # consumed

    # Second pass: yellows
    for i, g in enumerate(guess):
        if pattern[i] == "green":
            continue
        if g in answer_remaining:
            pattern[i] = "yellow"
            answer_remaining[answer_remaining.index(g)] = None  # consume one occurrence

    return pattern


def filter_vocabulary(vocabulary: list[str], guess: str, pattern: Pattern) -> list[str]:
    return [word for word in vocabulary if get_pattern(guess, word) == pattern]
