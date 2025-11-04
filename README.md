# AWS Cloud Task Orchestrator

A cloud-based task scheduling system implementing the Min-Min heuristic algorithm for optimal task distribution across multiple computing cores, deployed on AWS infrastructure.

## 1. Project Overview

This project demonstrates the deployment and execution of a task orchestration algorithm in the AWS cloud environment. The system reads task dependency graphs, computes optimal scheduling using the Min-Min algorithm, and stores execution plans in AWS S3, all orchestrated through AWS Lambda functions.

**Academic Context**: Developed as part of the ST7 Project at CentraleSupélec in collaboration with ANEO, focusing on cloud computing, distributed systems, and task scheduling optimization.

**For detailed information**, see the additional [documentation.pdf](documentation.pdf).

## 2. Architecture


**Data Flow**: Task graphs (JSON) → S3 input_data/ → Lambda (Min-Min algorithm) → S3 output_data/ → Execution plans (JSON)

**AWS Resources Naming**:
- S3 Bucket: `central-supelec-data-groupe<group_number>`
- Lambda Function: `ordonnanceur_groupe<group_number>`
- IAM Role: `LambdaS3_group<group_number>`

## 3. Technology Stack

**Cloud & Infrastructure**:
- AWS Lambda (serverless compute)
- AWS S3 (object storage)
- AWS CLI (deployment)

**Programming & Libraries**:
- Python 3.11
- NetworkX 3.4.2 (graph processing)
- boto3 (AWS SDK)
- memory-profiler 0.61.0 (performance analysis)
- psutil 7.0.0 (system utilities)

## 4. Project Structure

```
cloud/
├── v_1/                          # Initial implementation
│   ├── lambda_function.py
│   └── min_min.py
├── v_2_with_nmachines_and_graph_in_entries/  # Parameterized version
│   ├── lambda_function.py
│   ├── min_min.py
│   └── utilities.py
├── v_3_with_graph_generator/     # With graph generation
│   ├── lambda_function.py
│   ├── min_min.py
│   └── utilities.py
├── v_4_with_complexity_measure/  # Performance analysis
│   ├── lambda_function.py
│   ├── min_min.py
│   ├── utilities.py
│   └── complexity_measures.py
├── hello_world/                  # S3 integration test
└── networkx_and_mprofiler_layer/ # Lambda dependencies layer

graph_generator.py                # Local graph generation
min_min.py                        # Local algorithm version
draw_complexity_plots.py          # Performance visualization
```

## 5. Deployment

**Prerequisites**: AWS account, AWS CLI configured, Python 3.11+


### Quick Setup

```bash
# Configure AWS CLI
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Create S3 bucket and folders
BUCKET_NAME="central-supelec-data-groupe<group_number>"
aws s3 mb s3://${BUCKET_NAME} --region us-east-1
aws s3api put-object --bucket ${BUCKET_NAME} --key input_data/
aws s3api put-object --bucket ${BUCKET_NAME} --key output_data/

# Upload input graph
aws s3 cp graph.json s3://${BUCKET_NAME}/input_data/graph.json

# Package and deploy Lambda
cd cloud/v_3_with_graph_generator/
zip -r lambda_deployment.zip .

aws lambda create-function \
    --function-name ordonnanceur_groupe<group_number> \
    --runtime python3.11 \
    --role arn:aws:iam::<account_id>:role/LambdaS3_group<group_number> \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda_deployment.zip \
    --timeout 300 \
    --memory-size 512

# Attach dependencies layer
aws lambda update-function-configuration \
    --function-name ordonnanceur_groupe<group_number> \
    --layers arn:aws:lambda:us-east-1:<account_id>:layer:networkx_layer:1
```

## 6. Min-Min Algorithm

The Min-Min algorithm is a list scheduling heuristic that minimizes overall completion time (makespan) by iteratively selecting and assigning tasks with the minimum completion time.

**Algorithm Flow**:
1. Initialize unscheduled tasks and machine availability
2. Identify ready tasks (dependencies satisfied)
3. For each ready task, compute earliest completion time on each machine
4. Select task with minimum completion time (greedy choice)
5. Assign to optimal machine and update availability
6. Repeat until all tasks scheduled

**Complexity**: O(n² × m) where n = tasks, m = machines


## 7. Performance Analysis (v4)

Version 4 includes comprehensive performance profiling:
- Time complexity vs number of tasks (N)
- Time complexity vs number of machines (M)
- Memory usage vs number of tasks

**Sample Results**:

| Tasks | Time (s) | Machines |
|-------|----------|----------|
| 500   | 0.10     | 2        |
| 1000  | 0.26     | 2        |
| 2000  | 0.66     | 2        |
| 4000  | 2.06     | 2        |
| 8000  | 6.05     | 2        |

Performance scales O(n²) as expected. Visualize with: `python draw_complexity_plots.py`

## 8. Usage

### Execute Lambda Function

```bash
aws lambda invoke \
    --function-name ordonnanceur_groupe1 \
    --payload '{"num_machines": 4, "input_key": "input_data/graph.json", "output_key": "output_data/result.json"}' \
    response.json
```

### Retrieve Results

```bash
aws s3 cp s3://central-supelec-data-groupe1/output_data/result.json ./
aws s3 ls s3://central-supelec-data-groupe1/output_data/
```

## 9. Version Evolution :

- v1: Hardcoded parameters
- v2: Event-driven configuration
- v3: Integrated graph generation
- v4: Performance profiling

## 10. References

**NetworkX Documentation**: https://networkx.org/documentation/

## 10. Contributors

Ali Ait Mahiddine  
Ghiles Kemiche  
Noah Parisse  
Julien Dumortier  

---

*Academic project demonstrating cloud deployment, serverless architecture, and algorithmic optimization in distributed computing.*
