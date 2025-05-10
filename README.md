# kafka-pyspark-streaming-tutorial

![](/image/image-by-gpt-4o.png)

## 描述
用於學習 Kafka 的架構與概念，以及 PySpark Streaming 的實作。
主要流程為：
1. 模擬三個策略，分別將資料寫入 Kafka 的 Topic
2. 使用 PySpark Streaming 讀取 Kafka 的 Topic，並進行計算
3. 使用 PySpark Streaming 讀取 Kafka 的 Topic，並進行 Stream-Stream Join，再寫回 Kafka

---
### 目標

1. 熟悉 Kafka 的架構與概念
2. 熟悉 PySpark Streaming 的架構與概念
3. 熟悉 Stream-Stream Join 的架構與概念
4. 熟悉 PySpark Streaming 的實作

---
### 模組

1.	docker-compose：Kafka、Kafka-UI、Spark Master × 1、Spark Worker × 2
2.	Shell script：建立 8 個 Topic（A/B/C/D 的 _input 與 _output）
3.	Python Producer：隨機產生假資料送進 A/B/C 的 _input Topic
4.	PySpark Streaming
    •	strategy_job.py：讀取 X_input → 做簡單計算 → 寫回 X_output
    •	merge_c_d.py：Stream-Stream Join：C_output + D_input → 寫回 D_input_ready
---
### 專案結構

├── docker-compose.yml
├── scripts/
│   ├── create_topics.sh
│   └── producer.py
└── spark_jobs/
    ├── strategy_job.py
    └── merge_c_d.py

---
### 執行步驟

#### 1. 啟動 Kafka 叢集

```bash
# 建立必要目錄
mkdir -p .ivy2
chmod 777 .ivy2

# 啟動服務
docker-compose up -d
chmod +x scripts/create_topics.sh # 給予執行權限

./scripts/create_topics.sh      # 建立 Topic
```
#### 2. 啟動 Producer

```bash
# 確保有 Python 和 Kafka 套件
pip install kafka-python
python3 scripts/producer.py
```

#### 3. 執行 PySpark Job

```bash
chmod +x job_submit.sh
./job_submit.sh strategy_job.py --strategy A
./job_submit.sh strategy_job.py --strategy B
./job_submit.sh strategy_job.py --strategy C
```

#### 4. 執行 Stream-Stream Join

```bash
spark-submit --master spark://localhost:7077 --packages ... spark_jobs/merge_c_d.py
```

#### 5. 觀察結果

```bash
# 開啟 Kafka-UI
http://localhost:8084/

# 開啟 Spark Master Web UI
http://localhost:8081/
```

