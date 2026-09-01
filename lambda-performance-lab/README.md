# Lambda Performance Lab

A benchmarking project that measures how AWS Lambda memory configuration affects **execution performance, memory usage, and estimated compute cost** for a CPU-bound workload.

## Research Question

> **How does AWS Lambda memory configuration affect performance and cost?**

The same workload was tested on four Lambda memory configurations:

* 128 MB
* 256 MB
* 512 MB
* 1024 MB

Only the configured Lambda memory was changed between experiments.

---

## Architecture

```text
Local Machine
┌─────────────────────────────┐
│ benchmark/cpu.py            │
│                             │
│ Boto3                       │
│      │                      │
│      ▼                      │
│ Invoke AWS Lambda           │
└──────────────┬──────────────┘
               │
               ▼
AWS Lambda
┌─────────────────────────────┐
│ src/app.py                  │
│                             │
│ CPU-bound SHA-256 workload  │
│                             │
│ Measure execution           │
│ Measure memory usage        │
│ Return JSON                 │
└──────────────┬──────────────┘
               │
               ▼
Local Machine
┌─────────────────────────────┐
│ results/results.json        │
│                             │
│ benchmark/cpu.py            │
│ saves collected results     │
└─────────────────────────────┘
```

The Lambda function **does not save benchmark results**. It returns the measurements, and the local benchmark runner stores them in `results/results.json`.

---

## Project Structure

```text
lambda-performance-lab/
│
├── src/
│   └── app.py
│
├── benchmark/
│   ├── cpu.py
│   └── charts.py
│
├── results/
│   ├── results.json
│   ├── execution_time.png
│   ├── cost_comparison.png
│   ├── speedup.png
│   └── memory_usage.png
│
├── template.yaml
├── samconfig.toml
├── requirements.txt
├── README.md
├── diagnose.md
└── .gitignore
```

### File Responsibilities

| File                   | Purpose                                              |
| ---------------------- | ---------------------------------------------------- |
| `src/app.py`           | AWS Lambda handler and CPU workload                  |
| `benchmark/cpu.py`     | Locally invokes deployed Lambda and collects results |
| `benchmark/charts.py`  | Generates analysis charts from `results.json`        |
| `results/results.json` | Raw benchmark measurements                           |
| `results/*.png`        | Generated charts                                     |
| `template.yaml`        | AWS SAM infrastructure configuration                 |
| `samconfig.toml`       | Saved SAM deployment configuration                   |
| `diagnose.md`          | Development and troubleshooting log                  |
| `requirements.txt`     | Python dependencies                                  |

---

# Requirements

Install:

* Python 3.13+
* Docker
* AWS CLI
* AWS SAM CLI
* AWS account

Verify the installations:

```powershell
python --version
docker --version
aws --version
sam --version
```

---

# Setup

## 1. Clone the Repository

```powershell
git clone <repository-url>
cd lambda-performance-lab
```

## 2. Create Virtual Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# AWS Configuration

Configure the AWS CLI using an IAM identity with the required permissions:

```powershell
aws configure
```

The experiment uses:

```text
Region: ap-south-1
Architecture: x86_64
Runtime: Python 3.13
```

Verify the AWS identity:

```powershell
aws sts get-caller-identity
```

---

# Local Lambda Testing

AWS SAM and Docker are used to test the Lambda locally.

Build the application:

```powershell
sam build
```

Invoke the Lambda locally:

```powershell
sam local invoke BenchmarkFunction
```

Local execution is used to verify:

* Lambda handler correctness
* Workload execution
* Response structure
* Local development behavior

Local execution times are **not used as the final AWS benchmark data**.

---

# Deploy to AWS

Build the application:

```powershell
sam build
```

For the first deployment:

```powershell
sam deploy --guided
```

The project was configured with:

```text
Stack Name: lambda-performance-lab
Region: ap-south-1
Confirm changeset: Y
Allow SAM CLI IAM role creation: Y
Disable rollback: N
Save arguments to configuration file: Y
```

After the first guided deployment, the settings are stored in:

```text
samconfig.toml
```

Future deployments can use:

```powershell
sam build
sam deploy
```

---

# Verify Lambda Configuration

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
    --query "{Memory:MemorySize,Architecture:Architectures[0],Runtime:Runtime,Timeout:Timeout}"
```

The deployed experiment used:

```text
Runtime:     Python 3.13
Architecture: x86_64
Region:      ap-south-1
Timeout:     30 seconds
```

---

# Benchmark Runner

`benchmark/cpu.py` runs **locally**.

It uses Boto3 to invoke the deployed AWS Lambda.

Set the deployed function name in:

```text
benchmark/cpu.py
```

```python
FUNCTION_NAME = "YOUR_LAMBDA_FUNCTION_NAME"
```

Run the benchmark:

```powershell
py benchmark/cpu.py
```

The runner:

1. Invokes AWS Lambda.
2. Receives the Lambda response.
3. Performs 10 invocations.
4. Collects execution and memory measurements.
5. Saves the results locally.

The raw measurements are stored in:

```text
results/results.json
```

---

# CPU Workload

The Lambda runs a deterministic SHA-256 CPU workload.

The workload uses a fixed 10 MB input and performs repeated hashing operations.

The workload was calibrated after the initial 128 MB configuration timed out with the original workload.

The final benchmark workload performs 10 iterations, resulting in approximately 100 MB of hashing work.

The SHA-256 digest is returned with every invocation to verify that the same computation is performed across all configurations.

---

# Lambda Response

A successful invocation returns data similar to:

```json
{
  "duration_ms": 4375.58,
  "memory_limit_mb": "128",
  "memory_used_mb": 28.6,
  "request_id": "...",
  "digest": "..."
}
```

| Field             | Description                                   |
| ----------------- | --------------------------------------------- |
| `duration_ms`     | Measured workload execution time              |
| `memory_limit_mb` | Configured Lambda memory                      |
| `memory_used_mb`  | Observed memory usage                         |
| `request_id`      | Lambda invocation request ID                  |
| `digest`          | SHA-256 result used for workload verification |

---

# Benchmark Methodology

Four Lambda configurations were tested:

```text
128 MB
256 MB
512 MB
1024 MB
```

Each configuration was tested with **10 invocations**, resulting in:

```text
4 configurations × 10 runs = 40 AWS Lambda executions
```

The following were kept constant:

* Lambda source code
* Python runtime
* Architecture
* AWS region
* CPU workload
* Input data
* Number of runs
* Benchmark procedure

The primary experimental variable was:

```text
Lambda Memory Allocation
```

---

# Results

## Performance

|  Memory |    Average |     Median |        p95 |        p99 |
| ------: | ---------: | ---------: | ---------: | ---------: |
|  128 MB | 4147.03 ms | 4141.14 ms | 4259.10 ms | 4272.88 ms |
|  256 MB | 1930.65 ms | 1932.88 ms | 1952.60 ms | 1957.24 ms |
|  512 MB |  875.62 ms |  873.10 ms |  899.50 ms |  906.16 ms |
| 1024 MB |  517.86 ms |  518.57 ms |  530.82 ms |  534.89 ms |

---

## Memory Usage

|  Memory | Average Used | Maximum Used | Utilization |
| ------: | -----------: | -----------: | ----------: |
|  128 MB |     28.77 MB |     28.77 MB |      22.48% |
|  256 MB |     28.80 MB |     28.80 MB |      11.25% |
|  512 MB |     28.74 MB |     28.81 MB |       5.63% |
| 1024 MB |     28.47 MB |     28.49 MB |       2.78% |

The workload's actual memory usage remained approximately **28–29 MB** across all configurations.

---

# Speedup

Using 128 MB as the baseline:

|  Memory | Average Duration | Speedup vs 128 MB |
| ------: | ---------------: | ----------------: |
|  128 MB |       4147.03 ms |             1.00× |
|  256 MB |       1930.65 ms |             2.15× |
|  512 MB |        875.62 ms |             4.74× |
| 1024 MB |        517.86 ms |             8.01× |

The 1024 MB configuration completed the workload approximately **8× faster** than the 128 MB configuration.

---

# Estimated Compute Cost

Cost calculations use the measured execution time and allocated Lambda memory.

```text
GB-seconds =
Memory (GB) × Duration (seconds)
```

The analysis uses:

```text
$0.000020 per GB-second
```

for the x86_64 Lambda compute estimate.

|  Memory | Avg Duration | GB-seconds / Invocation | Estimated Cost / Invocation | Estimated Cost / 1M |
| ------: | -----------: | ----------------------: | --------------------------: | ------------------: |
|  128 MB |    4.14703 s |                 0.51838 |                 $0.00001037 |              $10.37 |
|  256 MB |    1.93065 s |                 0.48266 |                 $0.00000965 |               $9.65 |
|  512 MB |    0.87562 s |                 0.43781 |                 $0.00000876 |               $8.76 |
| 1024 MB |    0.51786 s |                 0.51786 |                 $0.00001036 |              $10.36 |

These are **estimated compute costs**, not exact AWS invoices. Request charges and other AWS account-level factors are not included.

---

# Performance vs Cost

Using 128 MB as the baseline:

|  Memory | Avg Duration | Speedup | Estimated Cost / 1M | Cost vs 128 MB |
| ------: | -----------: | ------: | ------------------: | -------------: |
|  128 MB |   4147.03 ms |   1.00× |              $10.37 |          1.00× |
|  256 MB |   1930.65 ms |   2.15× |               $9.65 |          0.93× |
|  512 MB |    875.62 ms |   4.74× |               $8.76 |          0.84× |
| 1024 MB |    517.86 ms |   8.01× |              $10.36 |          1.00× |

For this workload, **512 MB provides the lowest estimated compute cost while delivering a substantial performance improvement over lower memory configurations**.

1024 MB provides the fastest execution, but its estimated compute cost is approximately the same as the 128 MB configuration.

---

# Charts

Charts are generated from the raw `results/results.json` dataset using:

```text
benchmark/charts.py
```

Generate all charts:

```powershell
py benchmark/charts.py
```

Generated files:

```text
results/
├── execution_time.png
├── cost_comparison.png
├── speedup.png
└── memory_usage.png
```

The charts are derived from the recorded benchmark data rather than manually entered values.

---

# Local vs AWS Findings

Local SAM/Docker testing and real AWS Lambda execution produced substantially different execution times.

The original workload completed locally in under one second but timed out on the 128 MB AWS Lambda configuration.

The workload was subsequently reduced and successfully calibrated for the real AWS environment.

This demonstrated that:

> **Local SAM/Docker execution should be used for functional testing, not as the authoritative source for AWS Lambda performance measurements.**

The final performance dataset therefore comes exclusively from real AWS Lambda executions.

Detailed troubleshooting and diagnosis are documented in:

```text
diagnose.md
```

---

# Key Findings

For this CPU-bound workload:

* Increasing Lambda memory significantly reduced execution time.
* Actual memory usage remained almost constant at approximately 28–29 MB.
* 256 MB was approximately **2.15× faster** than 128 MB.
* 512 MB was approximately **4.74× faster** than 128 MB.
* 1024 MB was approximately **8.01× faster** than 128 MB.
* 512 MB produced the lowest estimated compute cost among the tested configurations.
* 1024 MB achieved the lowest execution time but did not provide the lowest estimated cost.

The results demonstrate why Lambda memory should not be selected solely based on the application's RAM requirements.

For CPU-bound workloads, increasing memory can also increase available compute capacity and significantly reduce execution time.

---

# Limitations

The results apply specifically to this workload and experimental environment.

Lambda performance can vary due to factors including:

* Cold starts
* Warm execution environments
* Runtime initialization
* AWS infrastructure conditions
* Region
* Runtime behavior
* Number of benchmark samples

Only 10 invocations were collected per configuration, so p95 and p99 values should be interpreted as descriptive measurements rather than statistically robust tail-latency estimates.

The cost analysis is an estimated compute-cost comparison and does not represent an exact AWS invoice.

---

# Troubleshooting

### Lambda Timeout

The original workload caused the 128 MB Lambda to reach the 30-second timeout.

CloudWatch showed:

```text
Memory Size: 128 MB
Max Memory Used: 51 MB
Duration: 30000 ms
Status: timeout
```

This indicated an execution-time/compute limitation rather than memory exhaustion.

CloudWatch logs can be inspected with:

```powershell
aws logs tail /aws/lambda/<FUNCTION_NAME> `
    --since 10m `
    --region ap-south-1
```

### Direct Lambda Invocation

To test the deployed function without the benchmark runner:

```powershell
aws lambda invoke `
    --function-name <FUNCTION_NAME> `
    --payload '{}' `
    response.json
```

Then:

```powershell
Get-Content response.json
```

Detailed diagnosis is documented in `diagnose.md`.

---

# Results Data

All raw benchmark measurements are stored in:

```text
results/results.json
```

The dataset contains:

```text
128 MB   → 10 runs
256 MB   → 10 runs
512 MB   → 10 runs
1024 MB  → 10 runs
```

Total:

```text
40 AWS Lambda benchmark runs
```

---

# Status

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
* [x] 128 MB benchmark
* [x] 256 MB benchmark
* [x] 512 MB benchmark
* [x] 1024 MB benchmark
* [x] Raw results collected
* [x] Performance analysis
* [x] Memory analysis
* [x] Cost analysis
* [x] Speedup analysis
* [x] Charts generated
* [x] Final findings
* [ ] Article
* [ ] Publish

---

# Article

Planned article:

> **I Tested AWS Lambda at 128MB, 256MB, 512MB and 1GB: Here's What Happened**

The article will cover:

* Experimental methodology
* AWS Lambda configuration
* Local vs AWS behavior
* Benchmark results
* Performance comparison
* Cost analysis
* Charts
* Findings
* Practical conclusions

---

# License

This project is intended for learning, experimentation, and reproducible AWS Lambda performance research.
