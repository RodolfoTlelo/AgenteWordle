"""
evaluate.py  –  Batch experiment runner
Runs the agent against N random words and computes performance metrics.

Metrics collected (as per project proposal):
  1. Average number of attempts to find the hidden word.
  2. Average decision time per turn (seconds).
  3. Win rate (solved within 6 attempts).
  4. Distribution of attempts (histogram).

Usage
-----
    python evaluate.py                   # 200 random words
    python evaluate.py --n 500           # 500 random words
    python evaluate.py --n 100 --seed 42 # reproducible run
    python evaluate.py --full            # entire vocabulary (~2500 words, slow)
"""

import sys
import os
import time
import random
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from agent import WordleAgent
from state import get_pattern


def run_experiment(n_words: int = 200, seed: int | None = None,
                   use_full: bool = False) -> dict:
    random.seed(seed)
    agent = WordleAgent()
    vocab = agent.answer_words

    sample = vocab if use_full else random.sample(vocab, min(n_words, len(vocab)))
    total = len(sample)

    results = []
    attempt_dist = {i: 0 for i in range(1, 8)}  # 7 = failed

    print(f"\nRunning experiment on {total} words...\n")

    for idx, secret in enumerate(sample, 1):
        agent.reset()
        turn_times = []
        solved = False

        for turn in range(1, agent.MAX_ATTEMPTS + 1):
            t0 = time.perf_counter()
            guess = agent.next_guess()
            t1 = time.perf_counter()
            turn_times.append(t1 - t0)

            pattern = get_pattern(guess, secret)
            agent.perceive(guess, pattern)

            if agent.state.solved:
                solved = True
                break

        attempts = agent.state.attempt_number
        bucket = attempts if solved else 7
        attempt_dist[bucket] += 1

        results.append({
            "secret": secret,
            "attempts": attempts,
            "solved": solved,
            "avg_turn_time_ms": round(sum(turn_times) / len(turn_times) * 1000, 3),
            "total_time_ms": round(sum(turn_times) * 1000, 3),
        })

        # Progress bar
        bar_len = 30
        filled = int(bar_len * idx / total)
        bar = "█" * filled + "░" * (bar_len - filled)
        pct = idx / total * 100
        print(f"\r  [{bar}] {pct:5.1f}%  ({idx}/{total})", end="", flush=True)

    print("\n")

    # ── Aggregate metrics ──────────────────────────────────────────────────
    solved_results = [r for r in results if r["solved"]]
    failed_results = [r for r in results if not r["solved"]]

    win_rate = len(solved_results) / total * 100
    avg_attempts = (sum(r["attempts"] for r in solved_results) / len(solved_results)
                    if solved_results else float("nan"))
    avg_turn_time = (sum(r["avg_turn_time_ms"] for r in results) / total)

    metrics = {
        "total_games": total,
        "solved": len(solved_results),
        "failed": len(failed_results),
        "win_rate_pct": round(win_rate, 2),
        "avg_attempts_when_solved": round(avg_attempts, 4),
        "avg_decision_time_ms": round(avg_turn_time, 3),
        "attempt_distribution": {
            str(k): v for k, v in attempt_dist.items()
        },
        "failed_words": [r["secret"] for r in failed_results],
    }

    return metrics, results


def print_metrics(metrics: dict) -> None:
    print("=" * 48)
    print("  EXPERIMENT RESULTS")
    print("=" * 48)
    print(f"  Total games           : {metrics['total_games']}")
    print(f"  Solved                : {metrics['solved']}")
    print(f"  Failed                : {metrics['failed']}")
    print(f"  Win rate              : {metrics['win_rate_pct']} %")
    print(f"  Avg attempts (solved) : {metrics['avg_attempts_when_solved']}")
    print(f"  Avg decision time     : {metrics['avg_decision_time_ms']} ms / turn")
    print()
    print("  Attempt distribution:")
    dist = metrics["attempt_distribution"]
    for k in ["1", "2", "3", "4", "5", "6"]:
        bar = "▪" * dist.get(k, 0)
        print(f"    {k} guesses : {dist.get(k, 0):4d}  {bar}")
    fails = dist.get("7", 0)
    if fails:
        print(f"    Failed   : {fails:4d}  {'▪' * fails}")
    if metrics["failed_words"]:
        print(f"\n  Failed words: {', '.join(metrics['failed_words'][:10])}"
              + ("..." if len(metrics["failed_words"]) > 10 else ""))
    print("=" * 48)


def save_results(metrics: dict, results: list, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    ts = int(time.time())
    metrics_path = os.path.join(output_dir, f"metrics_{ts}.json")
    results_path = os.path.join(output_dir, f"results_{ts}.json")

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Saved → {metrics_path}")
    print(f"  Saved → {results_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the Wordle Agent.")
    parser.add_argument("--n",    type=int,  default=200,  help="Number of words to test.")
    parser.add_argument("--seed", type=int,  default=None, help="Random seed.")
    parser.add_argument("--full", action="store_true",     help="Test entire vocabulary.")
    args = parser.parse_args()

    metrics, results = run_experiment(
        n_words=args.n, seed=args.seed, use_full=args.full
    )
    print_metrics(metrics)

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_results(metrics, results, os.path.join(base, "results"))
