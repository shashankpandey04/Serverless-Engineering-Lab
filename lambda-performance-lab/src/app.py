import hashlib
import os
import time


def get_memory_usage_mb():
    with open("/proc/self/status") as file:
        for line in file:
            if line.startswith("VmRSS:"):
                return round(int(line.split()[1]) / 1024, 2)

    return None


def lambda_handler(event, context):
    start = time.perf_counter()

    data = b"A" * 10_000_000
    digest = hashlib.sha256()

    for _ in range(10):
        digest.update(data)

    duration_ms = (time.perf_counter() - start) * 1000

    return {
        "duration_ms": round(duration_ms, 2),
        "memory_limit_mb": context.memory_limit_in_mb,
        "memory_used_mb": get_memory_usage_mb(),
        "request_id": context.aws_request_id,
        "digest": digest.hexdigest(),
    }