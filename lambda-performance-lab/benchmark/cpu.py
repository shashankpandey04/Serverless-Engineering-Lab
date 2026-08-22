import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

import boto3


FUNCTION_NAME = "BenchmarkFunction"
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

    if "FunctionError" in response:
        raise RuntimeError(
            f"Lambda execution failed: {response['FunctionError']}"
        )

    payload = response["Payload"].read()

    return json.loads(payload)


def save_results(results):
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_FILE.open("w") as file:
        json.dump(results, file, indent=2)


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