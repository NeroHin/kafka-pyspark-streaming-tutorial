# Kafka-PySpark Streaming Tutorial

![](/image/image-by-gpt-4o.png)

[中文版README](README_zh.md) | English

## Project Description
This is a tutorial project for learning Kafka and PySpark Streaming. Through hands-on practice, you will understand the architecture and concepts of Kafka, as well as how to use PySpark Streaming to process streaming data and perform Stream-Stream Join operations.

Main workflow:
1. Simulate three strategies (A, B, C, D), each writing data to Kafka Topics
2. Use PySpark Streaming to read data from Kafka Topics and perform calculations
3. Use PySpark Streaming to read from Kafka Topics, perform Stream-Stream Join, and write back to Kafka

![](/image/system-component_and_flow.png)

---
### Learning Objectives

1. Become familiar with Kafka architecture and concepts
2. Understand PySpark Streaming architecture and concepts
3. Master Stream-Stream Join architecture and concepts
4. Gain practical experience with PySpark Streaming implementation

---
### System Architecture

#### Data Flow
1. Producer generates mock data → Kafka Topic (A/B/C/D_input)
2. PySpark Streaming reads data → processes → writes back to Kafka Topic (A/B/C/D_output)
3. Special processing: C_output + D_input → Stream-Stream Join → D_input_ready

#### Main Modules

1. **Docker Container Environment**:
   - Kafka: Single-node KRaft mode (controller + broker)
   - Kafka-UI: Web interface for monitoring Kafka
   - Spark Master × 1
   - Spark Worker × 2

2. **Script Tools**:
   - `create_topics.sh`: Creates 8 Topics (A/B/C/D_input and A/B/C/D_output)
   - `producer.py`: Mock data generator that randomly generates data and sends it to A/B/C/D_input Topics
   - `job_submit.sh`: Tool script for submitting PySpark Jobs to the Spark cluster
   - `total-job-submit.sh`: One-click launcher for all PySpark Streaming Jobs

3. **PySpark Streaming Applications**:
   - `strategy_job.py`: Reads from X_input → performs simple calculations → writes to X_output
   - `merge_c_d.py`: Performs Stream-Stream Join: C_output + D_input → writes to D_input_ready

---
### Project Structure

```
├── docker-compose.yaml       # Container definition file
├── requirement.txt           # Python dependencies
├── image/                    # Image resources directory
├── data/                     # Data storage directory
├── .ivy2/                    # Spark dependency cache directory
├── scripts/                  # Tool scripts
│   ├── create_topics.sh      # Create Kafka Topics
│   ├── producer.py           # Mock data generator
│   ├── job_submit.sh         # Spark job submission tool
│   └── total-job-submit.sh   # One-click launcher for all Spark jobs
└── spark_jobs/               # PySpark jobs
    ├── strategy_job.py       # Strategy calculation job
    └── merge_c_d.py          # Stream-Stream Join job
```

---
### Data Processing Description

1. **Strategy Processing Flow**:
   - Read raw data from X_input
   - Calculate based on different strategies:
     - When value < 30: value × 2
     - When value between 30-60: value × 1.5 + 10
     - When value > 60: value squared ÷ 100
   - Write results to corresponding X_output

2. **Stream-Stream Join**:
   - Read data streams from C_output and D_input
   - Perform Inner Join within a time window (±5 minutes)
   - Write merged results to D_input_ready

---
### Execution Steps

#### 1. Start Kafka Cluster

```bash
# Create necessary directories
mkdir -p .ivy2
chmod 777 .ivy2

# Start services
docker-compose up -d
chmod +x scripts/create_topics.sh  # Grant execution permissions

./scripts/create_topics.sh  # Create Topics
```

#### 2. Start Producer

```bash
# Ensure Python and Kafka packages are installed
pip install kafka-python
python3 scripts/producer.py
```

#### 3. Run PySpark Jobs

Method 1: Run tasks separately
```bash
chmod +x scripts/job_submit.sh
./scripts/job_submit.sh strategy_job.py --strategies A B C D
./scripts/job_submit.sh merge_c_d.py
```

Method 2: Start all tasks with one command
```bash
chmod +x scripts/total-job-submit.sh
./scripts/total-job-submit.sh
```

#### 4. Observe Results

```bash
# Open Kafka-UI to view Topics and messages
http://localhost:8084/

# Open Spark Master Web UI to monitor jobs
http://localhost:8081/
```

#### 5. Stop Services

```bash
# Stop and remove all containers
docker-compose down
```

---
### Technical Details

- **Kafka**: Using KRaft mode (not ZooKeeper), version 7.6.0
- **Spark**: Using Bitnami Spark 3.5 image
- **Data Format**: JSON format, containing strategy, value, ts fields
- **Processing Mode**: Spark Structured Streaming with Kafka interface
- **Join Mode**: Stream-Stream Join within a time window (±5 minutes)

---
### Troubleshooting

1. **Ivy Directory Permission Issue**: Ensure .ivy2 directory has correct permissions with `chmod 777 .ivy2`
2. **Kafka Connection Issue**: Use `kafka:29092` within containers, use `localhost:9092` on local machine
3. **Spark Job Failure**: Check logs in Spark UI (http://localhost:8081/)

