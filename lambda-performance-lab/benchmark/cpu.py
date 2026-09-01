import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

import boto3


FUNCTION_NAME = "lambda-performance-lab-BenchmarkFunction-S8eaWcgRF767"
RUNS = 10

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_FILE = PROJECT_ROOT / "results" / "results.json"

lambda_client = boto3.client("lambda")


def invoke_lambda():
    response = lambda_client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=b"{}",
    )

    payload = response["Payload"].read()

    if "FunctionError" in response:
        error = json.loads(payload)
        raise RuntimeError(
            f"Lambda execution failed:\n"
            f"{json.dumps(error, indent=2)}"
        )

    return json.loads(payload)

def save_results(results):
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    if RESULTS_FILE.exists():
        with RESULTS_FILE.open("r") as file:
            existing_results = json.load(file)
    else:
        existing_results = {}

    if isinstance(existing_results, list):
        old_memory = existing_results[0]["memory_limit_mb"]
        existing_results = {
            old_memory: existing_results
        }

    memory = results[0]["memory_limit_mb"]
    existing_results[memory] = results

    with RESULTS_FILE.open("w") as file:
        json.dump(existing_results, file, indent=2)

def run_benchmark():
    results = []

    print(f"Running {RUNS} Lambda invocations...\n")

    for run in range(1, RUNS + 1):
        result = invoke_lambda()

        result["run"] = run
        result["timestamp"] = datetime.now(timezone.utc).isoformat()

        results.append(result)

        print(
            f"Run {run:02d} | "
            f"Duration: {result['duration_ms']} ms | "
            f"Memory: {result['memory_used_mb']} MB"
        )

    save_results(results)

    durations = [
        result["duration_ms"]
        for result in results
    ]

    print("\nBenchmark complete")
    print(f"Runs:    {len(results)}")
    print(f"Average: {mean(durations):.2f} ms")
    print(f"Median:  {median(durations):.2f} ms")
    print(f"Minimum: {min(durations):.2f} ms")
    print(f"Maximum: {max(durations):.2f} ms")

    print(f"\nResults saved to:")
    print(RESULTS_FILE)

    return results


if __name__ == "__main__":
    run_benchmark()