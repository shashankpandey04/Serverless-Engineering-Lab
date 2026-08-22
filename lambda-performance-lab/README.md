# Lambda Performance Lab

A benchmarking project that measures how different AWS Lambda memory configurations affect **execution performance, memory usage, and cost**.

The project runs the same Lambda workload with different memory allocations and uses a local benchmark runner to invoke the deployed Lambda repeatedly, collect its results, and analyze the measurements.

## Research Question

> **How do Lambda memory configurations affect performance and cost?**

AWS Lambda allows you to configure the memory available to a function.

An important detail is that Lambda also provides additional CPU capacity as memory allocation increases.

This creates an interesting performance-versus-cost trade-off:

```text
More Memory
     ↓
More CPU
     ↓
Potentially Faster Execution
     ↓
Higher Price per Unit of Execution
```

This project measures that trade-off instead of assuming that more memory is automatically better.

## What This Project Does

The experiment runs the **same Lambda function** using four memory configurations:

| Configuration |  Memory |
| ------------- | ------: |
| A             |  128 MB |
| B             |  256 MB |
| C             |  512 MB |
| D             | 1024 MB |

For each configuration, the benchmark runner:

1. Invokes the deployed AWS Lambda.
2. Receives the result returned by the Lambda.
3. Repeats the invocation multiple times.
4. Collects execution measurements.
5. Saves the measurements locally.
6. Calculates performance statistics.
7. Compares performance and cost across configurations.

The Lambda itself does **not** save benchmark results.

The Lambda measures its execution and returns the data to the runner.

```text
┌─────────────────────────────┐
│        Your Computer        │
│                             │
│     benchmark/cpu.py        │
│             │               │
│             │ Boto3         │
└─────────────┼───────────────┘
              │
              ▼
┌─────────────────────────────┐
│            AWS              │
│                             │
│      Lambda Function        │
│        src/app.py           │
│             │               │
│        Run workload         │
│             │               │
│        Measure execution    │
│             │               │
│        Return result        │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│        Your Computer        │
│                             │
│      cpu.py receives        │
│          the result         │
│              │              │
│              ▼              │
│      results/results.json   │
└─────────────────────────────┘
```

## Project Structure

```text
lambda-performance-lab/
│
├── src/
│   └── app.py
│
├── benchmark/
│   └── cpu
.py
│
├── results/
│   └── results.json
│
├── template.yaml
├── requirements.txt
├── README.md
└── .gitignore
```

### `src/app.py`

Contains the Lambda workload.

The Lambda:

* Executes the benchmark workload.
* Measures execution duration.
* Reads the Lambda memory limit.
* Measures process memory usage.
* Returns the measurements as JSON.

### `benchmarkcpur.py`

Runs locally on the developer's computer.

It:

* Uses Boto3 to invoke AWS Lambda.
* Runs multiple benchmark iterations.
* Receives the Lambda response.
* Adds local benchmark metadata.
* Calculates basic statistics.
* Saves the results locally.

### `results/results.json`

Contains the benchmark measurements returned by Lambda.

The results are stored locally because the benchmark runner is responsible for collecting and storing experimental data.

### `template.yaml`

Defines the Lambda infrastructure using AWS SAM.

### `requirements.txt`

Contains Python dependencies required by the benchmark runner.

## Current Lambda Workload

The current workload is CPU-bound.

The Lambda performs repeated SHA-256 hashing against a fixed dataset.

The purpose is to create a computational workload where differences in available CPU capacity can be observed as Lambda memory allocation changes.

The workload is intentionally deterministic.

The resulting hash is returned with every invocation so that the benchmark can verify that every memory configuration is performing the same computation.

## Lambda Response

Each Lambda invocation returns data similar to:

```json
{
  "duration_ms": 811.09,
  "memory_limit_mb": "128",
  "memory_used_mb": 28.41,
  "request_id": "example-request-id",
  "digest": "example-digest"
}
```

### Fields

| Field             | Description                                         |
| ----------------- | --------------------------------------------------- |
| `duration_ms`     | Time taken by the benchmark workload                |
| `memory_limit_mb` | Memory configured for the Lambda                    |
| `memory_used_mb`  | Memory used by the Lambda process                   |
| `request_id`      | AWS Lambda invocation identifier                    |
| `digest`          | SHA-256 result used to verify identical computation |

The actual request ID and digest values will differ between invocations.

## Local Development

The Lambda can be tested locally using AWS SAM and Docker before deploying it to AWS.

This is useful for verifying the Lambda code and benchmark workflow without using real AWS Lambda executions.

### Requirements

Install:

* Python
* Docker
* AWS CLI
* AWS SAM CLI

Verify the installations:

```powershell
python --version
docker --version
aws --version
sam --version
```

## Python Environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Local Lambda Testing

Build the SAM application:

```powershell
sam build
```

Invoke the Lambda locally:

```powershell
sam local invoke BenchmarkFunction
```

SAM runs the Lambda inside a Docker container that emulates the AWS Lambda runtime.

The local test is useful for verifying that the Lambda returns the expected benchmark data.

## AWS Configuration

The benchmark runner invokes the real AWS Lambda using Boto3.

Configure the AWS CLI with an IAM identity that has permission to use the required AWS services:

```powershell
aws configure
```

Verify the configured identity:

```powershell
aws sts get-caller-identity
```

The command should return the AWS account and IAM identity being used by the CLI.

## Deploying the Lambda

Build the project:

```powershell
sam build
```

Deploy it to AWS:

```powershell
sam deploy --guided
```

During the guided deployment, provide the desired AWS region and allow SAM to create the required deployment resources.

After deployment, SAM will create the Lambda function defined in `template.yaml`.

The actual AWS Lambda function name should then be used by `benchmarkcpur.py`.

## Running the Benchmark

Update the Lambda function name in:

```text
benchmarkcpu.pyy
```

Set:

```python
FUNCTION_NAME = "YOUR_LAMBDA_FUNCTION_NAME"
```

to the actual deployed Lambda function name.

Then run the benchmark locally:

```powershell
python benchmarkcpu.pyy
```

The runner invokes the Lambda multiple times.

For each invocation it receives the measurements returned by Lambda and stores them in:

```text
results/results.json
```

## Benchmark Flow

```text
Build Lambda
     ↓
Deploy to AWS
     ↓
Configure Lambda memory
     ↓
Run benchmark runner locally
     ↓
Boto3 invokes Lambda
     ↓
Lambda executes workload
     ↓
Lambda returns measurements
     ↓
Runner collects results
     ↓
Results saved locally
     ↓
Analyze results
```

## Benchmark Configuration

The experiment compares four Lambda memory allocations:

```text
128 MB
256 MB
512 MB
1024 MB
```

The Lambda workload remains unchanged between configurations.

The primary experimental variable is:

```text
Memory Allocation
```

The following should remain consistent:

* Lambda source code
* Runtime
* Architecture
* AWS region
* Workload
* Input data
* Number of iterations
* Benchmark procedure

## Benchmark Results

The final results will be populated from actual AWS Lambda executions.

### Performance

|  Memory | Average Duration |  Median |     p95 |     p99 |
| ------: | ---------------: | ------: | ------: | ------: |
|  128 MB |          Pending | Pending | Pending | Pending |
|  256 MB |          Pending | Pending | Pending | Pending |
|  512 MB |          Pending | Pending | Pending | Pending |
| 1024 MB |          Pending | Pending | Pending | Pending |

### Memory Usage

|  Memory | Average Memory Used | Maximum Memory Used | Utilization |
| ------: | ------------------: | ------------------: | ----------: |
|  128 MB |             Pending |             Pending |     Pending |
|  256 MB |             Pending |             Pending |     Pending |
|  512 MB |             Pending |             Pending |     Pending |
| 1024 MB |             Pending |             Pending |     Pending |

### Cost

|  Memory | Cost / Invocation | Cost / 1,000 Invocations | Cost / 1M Invocations |
| ------: | ----------------: | -----------------------: | --------------------: |
|  128 MB |           Pending |                  Pending |               Pending |
|  256 MB |           Pending |                  Pending |               Pending |
|  512 MB |           Pending |                  Pending |               Pending |
| 1024 MB |           Pending |                  Pending |               Pending |

### Performance vs Cost

|  Memory | Relative Performance | Relative Cost | Performance / Cost |
| ------: | -------------------: | ------------: | -----------------: |
|  128 MB |              Pending |       Pending |            Pending |
|  256 MB |              Pending |       Pending |            Pending |
|  512 MB |              Pending |       Pending |            Pending |
| 1024 MB |              Pending |       Pending |            Pending |

These values will be calculated from the actual benchmark dataset.

## Analysis

The benchmark is not intended to identify the configuration with the lowest execution time alone.

The analysis considers:

```text
Performance
     +
Memory Utilization
     +
Execution Cost
```

A higher-memory configuration may execute a workload significantly faster because it receives more CPU capacity.

However, higher memory also increases the cost of each unit of execution.

The goal is therefore to identify the configuration that provides the best balance for the tested workload.

## Findings

This section will be updated after the AWS benchmark has been completed.

### Execution Performance

**Pending benchmark results.**

### Memory Utilization

**Pending benchmark results.**

### Cost

**Pending benchmark results.**

### Best Configuration

**Pending benchmark results.**

### Key Observation

**Pending benchmark results.**

## Why the Results Matter

Lambda memory selection is often treated as a simple choice between:

```text
Cheaper
vs.
Faster
```

The relationship is more nuanced because increasing memory also increases available CPU capacity.

This experiment provides measured data for understanding that trade-off for the specific workload being tested.

The results should help answer a practical question:

> **What Lambda memory configuration provides the best balance between execution speed and cost for this workload?**

## Limitations

The results are experimental measurements and are not universal Lambda performance guarantees.

Performance can vary because of:

* AWS infrastructure conditions
* Cold starts
* Warm execution environments
* Runtime initialization
* Network conditions
* AWS region
* External service latency
* Runtime behavior

The benchmark therefore focuses on comparing configurations under the same experimental conditions.

## Reproducibility

The project keeps the Lambda code, infrastructure definition, benchmark runner, and collected results in the repository.

A developer can reproduce the experiment by:

1. Cloning the repository.
2. Installing the required tools.
3. Configuring AWS credentials.
4. Building the SAM application.
5. Deploying the Lambda.
6. Running the benchmark runner.
7. Analyzing the collected results.

## Future Experiments

The current implementation focuses on a CPU-bound workload.

The project can later be extended with:

* Memory-bound workloads
* I/O-bound workloads
* Cold-start benchmarks
* Different payload sizes
* Different runtimes
* ARM64 vs x86_64
* Different execution patterns
* Larger benchmark samples

These extensions can help determine whether the optimal Lambda memory configuration changes depending on workload characteristics.

## Article

The findings from this experiment will be documented in:

**I Tested AWS Lambda at 128MB, 256MB, 512MB and 1GB: Here's What Happened**

The article will include:

* Experimental methodology
* AWS environment
* Benchmark results
* Performance comparisons
* Cost analysis
* Charts
* Key findings
* Practical recommendations

## Status

**In Progress**

* [x] Define research question
* [x] Define memory configurations
* [x] Define CPU-bound workload
* [x] Create Lambda function
* [x] Create SAM template
* [x] Configure local Lambda testing
* [x] Create local benchmark runner
* [x] Verify Lambda locally
* [ ] Deploy Lambda to AWS
* [ ] Run AWS benchmark
* [ ] Collect benchmark dataset
* [ ] Calculate performance statistics
* [ ] Calculate Lambda costs
* [ ] Generate charts
* [ ] Complete analysis
* [ ] Write article
* [ ] Publish results

## License

This project is open source and intended for experimentation, learning, and reproducible AWS Lambda performance research.
