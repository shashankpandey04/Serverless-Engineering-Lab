# Serverless Engineering Lab

A collection of experiments, projects, and architecture studies focused on AWS Serverless.

This repository is my hands-on exploration of serverless architecture, from Lambda fundamentals and event-driven systems to production-grade architectures, resilience, observability, cost optimization, and developer tooling.

The goal is not simply to learn AWS services, but to understand **when to use them, how they behave under real workloads, what tradeoffs they introduce, and how different serverless components work together.**





## Learning Roadmap

### Month 1: Serverless Foundations

| Project                          | Focus                               | Status  |
| -------------------------------- | ----------------------------------- | ------- |
| [01] Lambda Performance Lab      | Lambda memory, performance and cost | Planned |
| [02] Serverless Image Processing | S3 + Lambda event processing        | Planned |
| [03] Serverless URL Shortener    | API Gateway + Lambda + DynamoDB     | Planned |
| [04] Serverless Scheduler        | EventBridge Scheduler + Lambda      | Planned |

### Month 2: Event-Driven Serverless

| Project                        | Focus                                    | Status  |
| ------------------------------ | ---------------------------------------- | ------- |
| [05] SQS Async Worker          | Asynchronous Lambda processing           | Planned |
| [06] SQS Retry & DLQ Lab       | Retries, failures and dead-letter queues | Planned |
| [07] SNS Fan-Out System        | SNS + SQS + Lambda fan-out               | Planned |
| [08] Event-Driven Order System | EventBridge + SQS architecture           | Planned |

### Month 3: Serverless Data & Workflows

| Project                          | Focus                                     | Status  |
| -------------------------------- | ----------------------------------------- | ------- |
| [09] DynamoDB Access Pattern Lab | Single-table thinking and access patterns | Planned |
| [10] DynamoDB GSI Experiment     | Global Secondary Indexes                  | Planned |
| [11] Step Functions Workflow     | Orchestration vs Lambda chaining          | Planned |
| [12] Serverless File Processing  | S3 + Step Functions + Lambda              | Planned |

### Month 4: Production Serverless

| Project                             | Focus                              | Status  |
| ----------------------------------- | ---------------------------------- | ------- |
| [13] Serverless Authentication      | Cognito + API Gateway + Lambda     | Planned |
| [14] Serverless Observability       | CloudWatch + X-Ray                 | Planned |
| [15] Serverless Resilience          | Failure handling and recovery      | Planned |
| [16] Serverless Cost & Architecture | Architecture and cost optimization | Planned |

### Month 5: Advanced Serverless Architecture

| Project                               | Focus                                    | Status  |
| ------------------------------------- | ---------------------------------------- | ------- |
| [17] Lambda vs Containers             | Serverless vs container workloads        | Planned |
| [18] Event-Driven Domain Architecture | Domain events and independent consumers  | Planned |
| [19] Serverless Production Platform   | Production-grade serverless architecture | Planned |
| [20] Open Source Serverless Tool      | Developer tooling for serverless         | Planned |

## What I Am Exploring

The projects in this repository cover:

* AWS Lambda
* Amazon API Gateway
* Amazon S3
* Amazon DynamoDB
* Amazon EventBridge
* Amazon EventBridge Scheduler
* Amazon SQS
* Amazon SNS
* AWS Step Functions
* Amazon Cognito
* Amazon CloudWatch
* AWS X-Ray
* AWS IAM
* Infrastructure as Code
* CI/CD
* Serverless security
* Reliability and resilience
* Performance optimization
* Cost optimization
* Event-driven architecture
* Domain-driven architecture
* Serverless vs containers

## Project Philosophy

Every project starts with a question.

Instead of building an application simply to demonstrate an AWS service, I try to investigate a specific engineering problem.

For example:

> How does Lambda memory configuration affect performance and cost?

or:

> When should Step Functions be used instead of chaining Lambda functions together?

or:

> What actually happens when an SQS-triggered Lambda repeatedly fails?

The projects are designed to answer these questions through implementation, experiments, measurements, and analysis.

## Experiments & Measurements

Where applicable, projects include real measurements rather than relying only on theoretical explanations.

Depending on the project, this may include:

* Execution duration
* Cold starts
* Throughput
* Latency
* Memory utilization
* Error rates
* Retry behavior
* Queue processing behavior
* Failure recovery
* Resource utilization
* AWS service costs
* Architecture tradeoffs

Results and benchmark data are kept alongside the relevant project.



Not every project will contain every directory. The structure depends on the experiment.

## Articles

Some projects will be accompanied by technical articles documenting the experiment, implementation, results, and lessons learned.

The articles will focus on **engineering findings rather than step-by-step AWS tutorials**.

Article links will be added here as projects are completed.

| Project | Article                              | Status  |
| ------- | ------------------------------------ | ------- |
| 01      | Lambda Performance Lab               | Planned |
| 02      | Serverless Image Processing Pipeline | Planned |
| 03      | Serverless URL Shortener             | Planned |
| 04      | EventBridge Scheduler                | Planned |
| 05      | SQS Async Worker                     | Planned |
| 06      | SQS Retry & DLQ                      | Planned |
| 07      | SNS Fan-Out                          | Planned |
| 08      | Event-Driven Order System            | Planned |
| 09      | DynamoDB Access Patterns             | Planned |
| 10      | DynamoDB GSI                         | Planned |
| 11      | Lambda Chaining vs Step Functions    | Planned |
| 12      | Serverless File Processing           | Planned |
| 13      | Serverless Authentication            | Planned |
| 14      | Serverless Observability             | Planned |
| 15      | Serverless Resilience                | Planned |
| 16      | Serverless Cost & Architecture       | Planned |
| 17      | Lambda vs Containers                 | Planned |
| 18      | Event-Driven Domain Architecture     | Planned |
| 19      | Serverless Production Platform       | Planned |
| 20      | Open Source Serverless Tool          | Planned |

## Flagship Projects

Not every experiment in this repository is intended to have the same depth.

Some projects will become deeper investigations with detailed benchmarks, architecture analysis, and technical articles.

The current flagship candidates are:

1. Lambda Performance Lab
2. SQS Retry & DLQ Lab
3. DynamoDB Access Pattern Lab
4. Lambda Chaining vs Step Functions
5. Serverless Resilience Lab
6. Serverless Production Platform

These may evolve as the experiments produce results.

## Technology

The primary platform for this repository is AWS.

Projects may additionally use:

* Python
* Docker
* AWS SAM
* AWS CDK where appropriate
* GitHub Actions
* pytest
* AWS CLI

The technology used in each project is documented in its individual README.

## Infrastructure & Cost

AWS resources can incur charges.

Projects are designed with cost awareness in mind, and unnecessary resources should be removed after experiments are completed.

Each project that creates billable AWS resources should document:

* Services used
* Resources created
* Expected cost considerations
* Cleanup instructions

**Always verify your AWS resources after completing an experiment and delete resources that are no longer required.**

## Current Progress

**Projects completed:** 0 / 20

**Flagship articles:** 0 / 6

**Open-source tools:** 0 / 1

This section will be updated as the repository progresses.

## Why This Repository Exists

Serverless is often presented as a collection of individual AWS services.

This repository is an attempt to understand the bigger picture.

How do these services behave individually?

How do they behave together?

What happens when something fails?

What does the architecture cost?

Where are the tradeoffs?

And most importantly:

> **When should I actually use serverless?**

That's what this lab is intended to explore.

## License

Unless otherwise specified, the code in this repository is available under the MIT License.
