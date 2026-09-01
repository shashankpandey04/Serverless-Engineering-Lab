# Diagnosis Log

This document records issues, observations, and debugging steps encountered while developing the Lambda Performance Lab.

The purpose is to maintain a technical record of problems encountered during development, particularly differences between the local SAM/Docker environment and the actual AWS Lambda environment.

---

# 1. Local Lambda vs AWS Lambda

## Local Environment

The Lambda was initially tested using AWS SAM and Docker.

Execution flow:

```text
SAM CLI
   ↓
Docker
   ↓
Local Lambda Runtime
   ↓
src/app.py
```

The local Lambda successfully completed the initial CPU workload.

Example local execution:

```json
{
  "duration_ms": 937.46,
  "memory_limit_mb": "128",
  "memory_used_mb": 28.17,
  "request_id": "...",
  "digest": "143853930a3eadd0fbcb380fa3be6319bdd1f3c9e18c35bd676be2a8f3fb56c5"
}
```

Another execution:

```json
{
  "duration_ms": 811.09,
  "memory_limit_mb": "128",
  "memory_used_mb": 28.41,
  "request_id": "...",
  "digest": "143853930a3eadd0fbcb380fa3be6319bdd1f3c9e18c35bd676be2a8f3fb56c5"
}
```

This confirmed that:

* The Lambda handler worked.
* The workload executed successfully.
* The response format was correct.
* The benchmark runner could parse the response.
* The workload produced a consistent digest.

---

# 2. AWS Deployment

The application was deployed to AWS using AWS SAM.

Deployment configuration:

| Property       | Value                    |
| -------------- | ------------------------ |
| Stack          | `lambda-performance-lab` |
| Region         | `ap-south-1`             |
| Runtime        | Python 3.13              |
| Initial Memory | 128 MB                   |
| Timeout        | 30 seconds               |

The deployed Lambda was:

```text
lambda-performance-lab-BenchmarkFunction-S8eaWcgRF767
```

The Lambda was successfully created and could be invoked through the AWS CLI.

---

# 3. First AWS Invocation Failure

The first benchmark attempt against the deployed Lambda failed.

The benchmark runner initially reported only:

```text
Lambda execution failed: Unhandled
```

The error handling in `cpu.py` was then improved to expose the actual Lambda response payload.

The actual error was:

```json
{
  "errorType": "Sandbox.Timedout",
  "errorMessage": "RequestId: ... Error: Task timed out after 30.00 seconds"
}
```

---

# 4. Direct AWS Invocation

To determine whether the problem was caused by the benchmark runner or by the Lambda itself, the function was invoked directly using the AWS CLI.

Command:

```powershell
aws lambda invoke `
    --function-name lambda-performance-lab-BenchmarkFunction-S8eaWcgRF767 `
    --payload '{}' `
    response.json
```

The invocation returned:

```json
{
    "StatusCode": 200,
    "FunctionError": "Unhandled",
    "ExecutedVersion": "$LATEST"
}
```

The response body contained:

```json
{
  "errorType": "Sandbox.Timedout",
  "errorMessage": "RequestId: ... Error: Task timed out after 30.00 seconds"
}
```

This confirmed that the failure occurred inside the deployed Lambda rather than in the benchmark runner.

---

# 5. CloudWatch Diagnosis

CloudWatch logs were inspected using:

```powershell
aws logs tail /aws/lambda/lambda-performance-lab-BenchmarkFunction-S8eaWcgRF767 `
    --since 10m `
    --region ap-south-1
```

The Lambda repeatedly reported:

```text
Duration: 30000.00 ms
Billed Duration: 30000 ms
Memory Size: 128 MB
Max Memory Used: 51 MB
Status: timeout
```

One execution also reported:

```text
Init Duration: 101.02 ms
```

The important observation was:

```text
Memory Size:     128 MB
Max Memory Used: 51 MB
Duration:        30000 ms
Status:          timeout
```

The Lambda was **not running out of memory**.

It was reaching the configured 30-second execution timeout.

---

# 6. Initial Workload

The original CPU workload was:

```python
data = b"A" * 10_000_000

for _ in range(100):
    digest.update(data)
```

This processes approximately:

```text
10 MB × 100
≈ 1 GB
```

of data through the SHA-256 workload.

The workload was intentionally CPU-heavy because the project investigates the relationship between Lambda memory allocation and performance.

---

# 7. Local vs AWS Performance Difference

The same workload behaved very differently between the local and AWS environments.

| Environment      | Memory | Result                |
| ---------------- | -----: | --------------------- |
| Local SAM/Docker | 128 MB | ~0.8–0.9 seconds      |
| AWS Lambda       | 128 MB | >30 seconds / timeout |

This demonstrated that local SAM/Docker execution should **not** be treated as a source of final Lambda performance measurements.

Local execution is useful for:

* Validating the Lambda code
* Testing the handler
* Testing the benchmark runner
* Detecting functional errors

The actual performance experiment must use **real AWS Lambda executions**.

---

# 8. Workload Calibration

The original workload was too heavy for the 128 MB Lambda configuration.

Instead of increasing the timeout to accommodate the workload, the workload was reduced so that all planned memory configurations can complete successfully within a reasonable execution time.

The original workload:

```python
for _ in range(100):
    digest.update(data)
```

was changed to:

```python
for _ in range(10):
    digest.update(data)
```

The approximate workload was therefore reduced from:

```text
~1 GB
```

to:

```text
~100 MB
```

The purpose of the adjustment was not to eliminate the CPU-bound nature of the experiment, but to create a workload that can be measured successfully across the planned configurations.

---

# 9. Successful AWS Execution After Calibration

After reducing the workload, the 128 MB Lambda successfully completed a real AWS invocation.

Result:

```json
{
  "duration_ms": 4375.58,
  "memory_limit_mb": "128",
  "memory_used_mb": 28.6,
  "request_id": "f3006b5b-963d-4385-a28c-d0abbdd940d2",
  "digest": "4a1208e65257e3b9e3c7d4fca19c2b3e886feef8182a3b6532c116a363f99de4"
}
```

Observed values:

| Metric            |       Value |
| ----------------- | ----------: |
| Memory allocation |      128 MB |
| Workload duration | 4,375.58 ms |
| Memory used       |    28.60 MB |
| Execution status  |     Success |

This confirmed that the calibrated workload can successfully execute on the lowest planned memory configuration.

---

# 10. Important Observation: Local vs AWS

The calibrated workload produced approximately:

```text
Local SAM/Docker
≈ 0.8–0.9 seconds
```

while the real AWS Lambda execution produced:

```text
AWS Lambda
≈ 4.38 seconds
```

This difference is expected to be investigated rather than normalized away.

The local environment and AWS Lambda environment have different underlying compute characteristics.

Therefore, the project will use:

> **AWS Lambda measurements as the authoritative performance dataset.**

Local SAM measurements are only used for development and functional validation.

---

# 11. Memory Usage vs Memory Allocation

The successful 128 MB execution reported:

```text
Memory allocation: 128 MB
Memory used:       28.6 MB
```

This is an important distinction.

The Lambda had:

```text
128 MB
```

available but the Python process reported approximately:

```text
28.6 MB
```

of memory usage.

Therefore, the experiment should not interpret the configured memory value as the amount of memory actually consumed by the workload.

The configured memory affects Lambda's available resources, while the measured memory usage describes the application's observed process memory.

---

# 12. Why Memory Configuration Matters

AWS Lambda memory configuration affects more than available RAM.

For CPU-bound workloads, increasing memory can also provide additional CPU capacity.

The experiment therefore expects a relationship similar to:

```text
Higher Memory
      ↓
More CPU Capacity
      ↓
Lower Execution Time
```

However:

```text
Higher Memory
      ↓
Higher Cost per Unit Time
```

Therefore, the goal is not simply to find the fastest configuration.

The goal is to investigate the trade-off between:

```text
Performance
     +
Memory
     +
Cost
```

---

# 13. Benchmark Configurations

The planned AWS experiment uses:

```text
128 MB
256 MB
512 MB
1024 MB
```

The following should remain constant:

* Lambda source code
* Runtime
* Architecture
* AWS region
* Workload
* Input data
* Benchmark procedure

The primary variable is:

```text
Lambda Memory Allocation
```

---

# 14. Benchmark Methodology

For each memory configuration:

```text
Deploy configuration
       ↓
Invoke Lambda repeatedly
       ↓
Collect returned measurements
       ↓
Save results locally
       ↓
Calculate statistics
```

The benchmark runner runs locally.

The Lambda runs on AWS.

```text
YOUR COMPUTER
────────────────────
benchmark/cpu.py
       │
       │ Boto3
       ▼
AWS
────────────────────
Lambda
src/app.py
       │
       │ return JSON
       ▼
YOUR COMPUTER
       │
       ▼
results/results.json
```

The Lambda itself does not write benchmark results to disk.

---

# 15. Planned Analysis

For each memory configuration, the experiment will calculate:

### Execution Performance

* Average duration
* Median duration
* Minimum duration
* Maximum duration
* p95
* p99

### Memory

* Average memory usage
* Maximum memory usage
* Memory utilization

### Cost

* Cost per invocation
* Estimated cost per 1,000 invocations
* Estimated cost per 1 million invocations

### Efficiency

The experiment will compare performance improvements against the additional execution cost introduced by higher memory allocations.

 have been measured under the same conditions.
