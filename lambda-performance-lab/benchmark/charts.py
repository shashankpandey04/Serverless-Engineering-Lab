import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
RESULTS_FILE = ROOT / "results" / "results.json"
OUTPUT_DIR = ROOT / "results"


PRICE_PER_GB_SECOND = 0.000020


def load_results():
    with RESULTS_FILE.open("r") as file:
        return json.load(file)


def calculate_summary(results):
    summary = {}

    for memory, runs in results.items():
        durations = np.array(
            [run["duration_ms"] for run in runs],
            dtype=float,
        )

        memory_used = np.array(
            [run["memory_used_mb"] for run in runs],
            dtype=float,
        )

        memory_mb = int(memory)

        avg_duration = durations.mean()

        gb_seconds = (memory_mb / 1024) * (avg_duration / 1000)

        cost_per_invocation = gb_seconds * PRICE_PER_GB_SECOND

        summary[memory_mb] = {
            "average_duration": avg_duration,
            "average_memory_used": memory_used.mean(),
            "max_memory_used": memory_used.max(),
            "cost_per_invocation": cost_per_invocation,
        }

    return dict(sorted(summary.items()))


def save_chart(filename):
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()


def execution_time_chart(summary):
    memory = list(summary.keys())
    duration = [summary[m]["average_duration"] for m in memory]

    plt.figure(figsize=(8, 5))
    plt.bar([str(m) for m in memory], duration)

    plt.title("AWS Lambda Memory vs Average Execution Time")
    plt.xlabel("Lambda Memory (MB)")
    plt.ylabel("Average Execution Time (ms)")

    save_chart("execution_time.png")


def cost_chart(summary):
    memory = list(summary.keys())
    cost = [
        summary[m]["cost_per_invocation"] * 1_000_000
        for m in memory
    ]

    plt.figure(figsize=(8, 5))
    plt.bar([str(m) for m in memory], cost)

    plt.title("AWS Lambda Memory vs Estimated Cost")
    plt.xlabel("Lambda Memory (MB)")
    plt.ylabel("Estimated Compute Cost per 1M Invocations (USD)")

    save_chart("cost_comparison.png")


def speedup_chart(summary):
    memory = list(summary.keys())

    baseline = summary[128]["average_duration"]

    speedup = [
        baseline / summary[m]["average_duration"]
        for m in memory
    ]

    plt.figure(figsize=(8, 5))
    plt.bar([str(m) for m in memory], speedup)

    plt.title("AWS Lambda Memory vs Speedup")
    plt.xlabel("Lambda Memory (MB)")
    plt.ylabel("Speedup vs 128 MB (×)")

    save_chart("speedup.png")


def memory_usage_chart(summary):
    memory = list(summary.keys())
    usage = [summary[m]["average_memory_used"] for m in memory]

    plt.figure(figsize=(8, 5))
    plt.bar([str(m) for m in memory], usage)

    plt.title("AWS Lambda Memory vs Average Memory Used")
    plt.xlabel("Lambda Memory (MB)")
    plt.ylabel("Average Memory Used (MB)")

    save_chart("memory_usage.png")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = load_results()
    summary = calculate_summary(results)

    execution_time_chart(summary)
    cost_chart(summary)
    speedup_chart(summary)
    memory_usage_chart(summary)

    print("Charts generated:")
    print(" - results/execution_time.png")
    print(" - results/cost_comparison.png")
    print(" - results/speedup.png")
    print(" - results/memory_usage.png")


if __name__ == "__main__":
    main()