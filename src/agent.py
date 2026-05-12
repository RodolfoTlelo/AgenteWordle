from state import AgentState, Pattern, filter_vocabulary
from decision import choose_action
from vocabulary import load_vocabulary


class WordleAgent:

    MAX_ATTEMPTS = 6

    def __init__(self, vocabulary_path: str | None = None):
        self.answer_words, self.probe_words = load_vocabulary(vocabulary_path)
        # V starts as the full answer set
        self.state = AgentState(vocabulary=list(self.answer_words))
        self._last_guess: str | None = None

        print(f"[Agent] Answer words: {len(self.answer_words)} | "
              f"Probe vocabulary: {len(self.probe_words)}")

    # ------------------------------------------------------------------
    # Perception
    # ------------------------------------------------------------------

    def perceive(self, guess: str, pattern: Pattern) -> None:
        """Update state after receiving color feedback from the environment."""
        if len(pattern) != 5:
            raise ValueError("Pattern must contain exactly 5 color values.")
        guess = guess.lower()
        self.state.history.append((guess, list(pattern)))
        self.state.vocabulary = filter_vocabulary(self.state.vocabulary, guess, pattern)

    # ------------------------------------------------------------------
    # Decision → Action
    # ------------------------------------------------------------------

    def next_guess(self) -> str:
        """Return the agent's best next word based on current state."""
        if self.state.solved:
            raise RuntimeError("Game already solved.")
        if self.state.attempt_number >= self.MAX_ATTEMPTS:
            raise RuntimeError("Maximum attempts reached.")
        if not self.state.vocabulary:
            raise RuntimeError("No candidates remaining – inconsistent feedback?")

        guess = choose_action(self.state, self.probe_words)
        self._last_guess = guess
        return guess

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset agent for a new game."""
        self.state = AgentState(vocabulary=list(self.answer_words))
        self._last_guess = None

    def __repr__(self) -> str:
        return (f"WordleAgent("
                f"candidates={self.state.candidates_left}, "
                f"attempt={self.state.attempt_number})")
