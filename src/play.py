import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import WordleAgent
from state import get_pattern

RESET  = "\033[0m"
GREEN  = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GRAY   = "\033[100m\033[37m"
BOLD   = "\033[1m"

COLOR_MAP = {"green": GREEN, "yellow": YELLOW, "gray": GRAY}
SHORT_MAP = {"g": "green", "y": "yellow", "b": "gray",
             "gray": "gray", "green": "green", "yellow": "yellow"}


def render_pattern(word: str, pattern: list) -> str:
    parts = []
    for letter, color in zip(word.upper(), pattern):
        c = COLOR_MAP.get(color, RESET)
        parts.append(f"{c} {letter} {RESET}")
    return " ".join(parts)


def print_board(agent: WordleAgent) -> None:
    print()
    for word, pattern in agent.state.history:
        print("  " + render_pattern(word, pattern))
    print()


# ── Auto mode ─────────────────────────────────────────────────────────────────

def run_auto(secret: str | None = None, silent: bool = False) -> dict:
    agent = WordleAgent()

    pool = agent.answer_words  # only guess from valid answers
    if secret is None:
        secret = random.choice(pool)
    secret = secret.lower()

    if secret not in agent.probe_words:
        print(f"⚠  '{secret}' is not in the vocabulary.")
        sys.exit(1)

    # If secret isn't in answer_words, add it so the agent can find it
    if secret not in agent.answer_words:
        agent.answer_words.append(secret)
        agent.reset()

    if not silent:
        print(f"\n{'='*44}")
        print(f"  AUTO MODE  |  Secret: {'?' * 5}  (hidden)")
        print(f"{'='*44}\n")

    solved = False
    for turn in range(1, agent.MAX_ATTEMPTS + 1):
        guess = agent.next_guess()
        pattern = get_pattern(guess, secret)
        agent.perceive(guess, pattern)

        if not silent:
            print(f"  Turn {turn}: {render_pattern(guess, pattern)}"
                  f"  [{guess.upper()}]  |  candidates left: {agent.state.candidates_left}")

        if agent.state.solved:
            solved = True
            break

    if not silent:
        print()
        if solved:
            print(f"Solved '{secret.upper()}' in {agent.state.attempt_number} attempt(s)!\n")
        else:
            print(f"Failed. Secret was: {secret.upper()}\n")

    return {"secret": secret, "attempts": agent.state.attempt_number, "solved": solved}


# ── Interactive mode ──────────────────────────────────────────────────────────

def parse_feedback(raw: str) -> list[str] | None:
    raw = raw.strip().lower()
    tokens = raw.split() if " " in raw else list(raw.replace(",", ""))
    if len(tokens) != 5:
        return None
    result = []
    for t in tokens:
        mapped = SHORT_MAP.get(t)
        if mapped is None:
            return None
        result.append(mapped)
    return result


def run_interactive() -> None:
    agent = WordleAgent()
    print(f"\n{'='*52}")
    print(f"  {BOLD}WORDLE AGENT  –  Assisted Play{RESET}")
    print(f"  Vocabulary: {len(agent.probe_words):,} valid words")
    print(f"  Answer pool: {len(agent.answer_words):,} possible answers")
    print()
    print("  Feedback per letter:")
    print(f"    {GREEN} G {RESET} = green  (correct position)")
    print(f"    {YELLOW} Y {RESET} = yellow (wrong position)")
    print(f"    {GRAY} B {RESET} = gray   (not in word)")
    print(f"\n  Enter as: g y b b g  or  gybgg")
    print(f"{'='*52}\n")

    for turn in range(1, agent.MAX_ATTEMPTS + 1):
        guess = agent.next_guess()
        print(f"  ── Turn {turn}/6 {'─'*34}")
        print(f"  {BOLD}Suggestion → {guess.upper()}{RESET}")
        print(f"  Candidates remaining: {agent.state.candidates_left:,}")
        print()

        while True:
            raw = input("  Feedback (or 'q' to quit): ").strip()
            if raw.lower() == "q":
                print("\n  Goodbye!\n")
                return
            pattern = parse_feedback(raw)
            if pattern:
                break
            print("  ⚠  Use 5 chars: g/y/b  e.g. 'gbygb' or 'g b y g b'")

        agent.perceive(guess, pattern)
        print_board(agent)

        if agent.state.solved:
            print(f"Solved in {turn} attempt(s)!\n")
            return

    print("Could not solve in 6 attempts.\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--auto" in sys.argv:
        secret_arg = None
        if "--secret" in sys.argv:
            idx = sys.argv.index("--secret")
            if idx + 1 < len(sys.argv):
                secret_arg = sys.argv[idx + 1]
        run_auto(secret=secret_arg)

    elif "--today" in sys.argv:
        # Just show the first recommended guess
        agent = WordleAgent()
        from decision import FIRST_GUESS
        print(f"\n  Today's opening guess: {BOLD}{FIRST_GUESS.upper()}{RESET}\n")

    else:
        run_interactive()
