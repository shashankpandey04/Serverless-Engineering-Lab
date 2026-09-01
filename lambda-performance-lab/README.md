# Lambda Performance Lab

A benchmarking project to measure how AWS Lambda memory configuration affects **execution performance, memory usage, and cost**.

## Research Question

> **How do Lambda memory configurations affect performance and cost?**

The experiment runs the same CPU-bound workload using:

* 128 MB
* 256 MB
* 512 MB
* 1024 MB

Only the Lambda memory configuration changes between experiments.

## Architecture

```text
Your PC
┌─────────────────────────┐
│ benchmark/cpu.py        │
│                         │
│ Boto3 → invoke Lambda   │
└────────────┬────────────┘
             │
             ▼
AWS Lambda
┌─────────────────────────┐
│ src/app.py              │
│                         │
│ Run CPU workload        │
│ Measure execution       │
│ Measure memory          │
│ Return JSON             │
└────────────┬────────────┘
             │
             ▼
Your PC
┌─────────────────────────┐
│ results/results.json    │
└─────────────────────────┘
```

The Lambda **does not save results**. It returns measurements to the local benchmark script, which saves them locally.

## Project Structure

```text
lambda-performance-lab/
│
├── src/
│   └── app.py
│
├── benchmark/
│   └── cpu.py
│
├── results/
│   └── results.json
│
├── template.yaml
├── samconfig.toml
├── requirements.txt
├── README.md
├── diagnose.md
└── .gitignore
```

### Files

| File                   | Purpose                             |
| ---------------------- | ----------------------------------- |
| `src/app.py`           | Lambda function and CPU workload    |
| `benchmark/cpu.py`     | Local benchmark runner using Boto3  |
| `results/results.json` | Locally collected benchmark data    |
| `template.yaml`        | AWS SAM infrastructure definition   |
| `samconfig.toml`       | Saved SAM deployment configuration  |
| `diagnose.md`          | Development and troubleshooting log |
| `requirements.txt`     | Python dependencies                 |

## Requirements

Install:

* Python 3.13+
* Docker
* AWS CLI
* AWS SAM CLI
* An AWS account

Verify:

```powershell
python --version
docker --version
aws --version
sam --version
```

## Setup

### 1. Clone the repository

```powershell
git clone <repository-url>
cd lambda-performance-lab
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## AWS Configuration

Configure the AWS CLI using an IAM identity with permission to deploy and invoke the required resources:

```powershell
aws configure
```

Set the region to the region used for the experiment, for example:

```text
ap-south-1
```

Verify the configuration:

```powershell
aws sts get-caller-identity
```

## Local Lambda Testing

Local testing uses **AWS SAM + Docker**.

Build the project:

```powershell
sam build
```

Invoke the Lambda locally:

```powershell
sam local invoke BenchmarkFunction
```

This validates the Lambda code and response format before using real AWS Lambda executions.

**Local performance numbers are not used as the final benchmark data.**

## Deploy to AWS

The Lambda is deployed using AWS SAM.

Build:

```powershell
sam build
```

First deployment:

```powershell
sam deploy --guided
```

Recommended configuration:

```text
Stack Name: lambda-performance-lab
AWS Region: ap-south-1
Confirm changeset: Y
Allow SAM CLI IAM role creation: Y
Disable rollback: N
Save arguments to configuration file: Y
```

After the first deployment, `samconfig.toml` stores the deployment configuration.

Future deployments can use:

```powershell
sam build
sam deploy
```

## Verify the Lambda

List the deployed function:

```powershell
aws lambda list-functions `
    --region ap-south-1 `
    --query "Functions[?starts_with(FunctionName, 'lambda-performance-lab')].{Name:FunctionName,Memory:MemorySize,Runtime:Runtime}" `
    --output table
```

Check the configuration:

```powershell
aws lambda get-function-configuration `
    --function-name <FUNCTION_NAME> `
    --query "{Memory:MemorySize,Runtime:Runtime,Timeout:Timeout}"
```

## Run the Benchmark

`benchmark/cpu.py` runs **locally** and invokes the deployed Lambda using Boto3.

Set the deployed Lambda name in:

```text
benchmark/cpu.py
```

```python
FUNCTION_NAME = "YOUR_LAMBDA_FUNCTION_NAME"
```

Then run:

```powershell
python benchmark\cpu.py
```

The runner:

1. Invokes the AWS Lambda.
2. Receives the Lambda's JSON response.
3. Repeats the benchmark.
4. Adds local run metadata.
5. Calculates basic statistics.
6. Saves the measurements to `results/results.json`.

## Current CPU Workload

The Lambda runs a deterministic SHA-256 workload.

The workload uses a fixed 10 MB dataset and performs repeated hashing operations.

The resulting SHA-256 digest is returned with every invocation.

The digest is used to verify that every benchmark configuration performs the same computation.

## Lambda Response

A successful invocation returns:

```json
{
  "duration_ms": 4375.58,
  "memory_limit_mb": "128",
  "memory_used_mb": 28.6,
  "request_id": "...",
  "digest": "..."
}
```

| Field             | Meaning                                  |
| ----------------- | ---------------------------------------- |
| `duration_ms`     | Time measured for the workload           |
| `memory_limit_mb` | Configured Lambda memory                 |
| `memory_used_mb`  | Observed process memory                  |
| `request_id`      | Lambda invocation ID                     |
| `digest`          | SHA-256 result for workload verification |

## Benchmark Procedure

The experiment compares:

```text
128 MB
256 MB
512 MB
1024 MB
```

For each configuration:

```text
Change MemorySize
      ↓
sam build
      ↓
sam deploy
      ↓
Verify configuration
      ↓
Run benchmark
      ↓
Save results locally
```

The following remain unchanged:

* Lambda code
* Python runtime
* Architecture
* AWS region
* CPU workload
* Input data
* Number of benchmark runs
* Benchmark procedure

This keeps **memory allocation as the primary experimental variable**.

## Results

Final results will be populated from real AWS Lambda executions.
### Performance

|  Memory |    Average |     Median |        p95 |        p99 |
| ------: | ---------: | ---------: | ---------: | ---------: |
|  128 MB | 4147.03 ms | 4141.14 ms | 4259.10 ms | 4272.88 ms |
|  256 MB | 1930.65 ms | 1932.88 ms | 1952.60 ms | 1957.24 ms |
|  512 MB |  875.62 ms |  873.10 ms |  899.50 ms |  906.16 ms |
| 1024 MB |  517.86 ms |  518.57 ms |  530.82 ms |  534.89 ms |

### Memory Usage

|  Memory | Average Used | Maximum Used | Utilization |
| ------: | -----------: | -----------: | ----------: |
|  128 MB |     28.77 MB |     28.77 MB |      22.48% |
|  256 MB |     28.80 MB |     28.80 MB |      11.25% |
|  512 MB |     28.74 MB |     28.81 MB |       5.63% |
| 1024 MB |     28.47 MB |     28.49 MB |       2.78% |






### Cost

|  Memory | Cost / Invocation | Cost / 1K | Cost / 1M |
| ------: | ----------------: | --------: | --------: |
|  128 MB |           Pending |   Pending |   Pending |
|  256 MB |           Pending |   Pending |   Pending |
|  512 MB |           Pending |   Pending |   Pending |
| 1024 MB |           Pending |   Pending |   Pending |

### Performance vs Cost

|  Memory | Relative Performance | Relative Cost | Efficiency |
| ------: | -------------------: | ------------: | ---------: |
|  128 MB |              Pending |       Pending |    Pending |
|  256 MB |              Pending |       Pending |    Pending |
|  512 MB |              Pending |       Pending |    Pending |
| 1024 MB |              Pending |       Pending |    Pending |

## Current Results

### 128 MB Baseline

The first successful AWS benchmark contains **10 runs**.

Observed values:

* Average duration: approximately **4.15 seconds**
* Median duration: approximately **4.12 seconds**
* Minimum: **4.056 seconds**
* Maximum: **4.276 seconds**
* Memory used: approximately **28.77 MB**
* Successful runs: **10/10**

The complete raw measurements are stored in:

```text
results/results.json
```

## Local vs AWS

Local SAM/Docker testing is used for **correctness and development**.

It is not used as the authoritative performance dataset.

The same workload initially behaved very differently locally and on AWS. The original workload completed locally in under one second but timed out at 128 MB on AWS.

The workload was therefore reduced and successfully calibrated on the 128 MB AWS Lambda configuration.

See `diagnose.md` for the complete debugging record.

## Analysis

The experiment evaluates three primary factors:

```text
Performance
     +
Memory Usage
     +
Cost
```

The goal is not simply to find the fastest Lambda.

The goal is to determine:

> **Which memory configuration provides the best performance-to-cost trade-off for this CPU-bound workload?**

## Limitations

Results are specific to the tested workload and environment.

Lambda performance can vary due to factors including:

* Cold starts
* Warm execution environments
* Runtime initialization
* AWS infrastructure conditions
* Region
* Runtime behavior

The experiment therefore focuses on comparing configurations under consistent conditions.

## Article

### I Tested AWS Lambda at 128MB, 256MB, 512MB and 1GB: Here's What Happened

The final article will document:

* Experimental methodology
* AWS configuration
* Raw benchmark results
* Performance comparison
* Cost analysis
* Charts
* Findings
* Practical conclusions

## Status

* [x] Research question defined
* [x] Project structure created
* [x] Lambda implemented
* [x] SAM template created
* [x] Local Lambda testing
* [x] Benchmark runner created
* [x] AWS CLI configured
* [x] SAM CLI configured
* [x] Lambda deployed
* [x] AWS timeout diagnosed
* [x] Workload calibrated
* [x] 128 MB baseline collected
* [x] 256 MB benchmark
* [x] 512 MB benchmark
* [x] 1024 MB benchmark
* [ ] Final statistical analysis
* [ ] Cost analysis
* [ ] Charts
* [ ] Final findings
* [ ] Article
* [ ] Publish

## License

This project is intended for learning, experimentation, and reproducible AWS Lambda performance research.
