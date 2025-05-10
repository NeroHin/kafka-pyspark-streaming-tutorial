# kafka-pyspark-streaming-tutorial

![](/image/image-by-gpt-4o.png)

[English](README.md) | 中文版

## 專案描述
這是一個用於學習 Kafka 和 PySpark Streaming 的教學專案。透過實際操作，您將理解 Kafka 架構與概念，以及如何使用 PySpark Streaming 處理流式數據和執行 Stream-Stream Join 操作。

主要流程為：
1. 模擬三個策略（A、B、C），分別將資料寫入 Kafka 的 Topic
2. 使用 PySpark Streaming 讀取 Kafka 的 Topic，並進行計算
3. 使用 PySpark Streaming 讀取 Kafka 的 Topic，並進行 Stream-Stream Join，再寫回 Kafka

![](/image/system-component_and_flow.png)

---
### 學習目標

1. 熟悉 Kafka 的架構與概念
2. 熟悉 PySpark Streaming 的架構與概念
3. 熟悉 Stream-Stream Join 的架構與概念
4. 熟悉 PySpark Streaming 的實作

---
### 系統架構

#### 資料流向
1. Producer 產生假資料 → Kafka Topic (A/B/C/D_input)
2. PySpark Streaming 讀取資料 → 處理 → 寫回 Kafka Topic (A/B/C/D_output)
3. 特別處理：C_output + D_input → Stream-Stream Join → D_input_ready

#### 主要模組

1. **Docker 容器環境**：
   - Kafka：單節點 KRaft 模式（controller + broker）
   - Kafka-UI：提供 Web 界面監控 Kafka
   - Spark Master × 1
   - Spark Worker × 2

2. **腳本工具**：
   - `create_topics.sh`：建立 8 個 Topic（A/B/C/D 的 _input 與 _output）
   - `producer.py`：模擬資料產生器，隨機產生假資料送進 A/B/C/D 的 _input Topic
   - `job_submit.sh`：提交 PySpark Job 到 Spark 叢集的工具腳本
   - `total-job-submit.sh`：一鍵啟動所有 PySpark Streaming Job

3. **PySpark Streaming 應用**：
   - `strategy_job.py`：讀取 X_input → 做簡單計算 → 寫回 X_output 
   - `merge_c_d.py`：執行 Stream-Stream Join：C_output + D_input → 寫回 D_input_ready

---
### 專案結構

```
├── docker-compose.yaml       # 容器定義檔
├── requirement.txt           # Python 依賴套件
├── image/                    # 圖片資源目錄
├── data/                     # 資料儲存目錄
├── .ivy2/                    # Spark 依賴包快取目錄
├── scripts/                  # 工具腳本
│   ├── create_topics.sh      # 建立 Kafka Topics
│   ├── producer.py           # 假資料產生器
│   ├── job_submit.sh         # Spark 任務提交工具
│   └── total-job-submit.sh   # 一鍵啟動所有 Spark 任務
└── spark_jobs/               # PySpark 任務
    ├── strategy_job.py       # 策略計算任務
    └── merge_c_d.py          # Stream-Stream Join 任務
```

---
### 資料流處理說明

1. **策略處理流程**：
   - 從 X_input 讀取原始數據
   - 根據不同策略進行計算：
     - 當數值 < 30：值 × 2
     - 當數值介於 30-60：值 × 1.5 + 10
     - 當數值 > 60：值的平方 ÷ 100
   - 將結果寫入對應的 X_output

2. **Stream-Stream Join**：
   - 讀取 C_output 和 D_input 的數據流
   - 在時間窗口內（±5分鐘）進行 Inner Join
   - 合併結果寫入 D_input_ready

---
### 執行步驟

#### 1. 啟動 Kafka 叢集

```bash
# 建立必要目錄
mkdir -p .ivy2
chmod 777 .ivy2

# 啟動服務
docker-compose up -d
chmod +x scripts/create_topics.sh  # 給予執行權限

./scripts/create_topics.sh  # 建立 Topic
```

#### 2. 啟動 Producer

```bash
# 確保有 Python 和 Kafka 套件
pip install kafka-python
python3 scripts/producer.py
```

#### 3. 執行 PySpark Job

方法一：分別執行各個任務
```bash
chmod +x scripts/job_submit.sh
./scripts/job_submit.sh strategy_job.py --strategies A B C D
./scripts/job_submit.sh merge_c_d.py
```

方法二：一鍵啟動所有任務
```bash
chmod +x scripts/total-job-submit.sh
./scripts/total-job-submit.sh
```

#### 4. 觀察結果

```bash
# 開啟 Kafka-UI 查看 Topic 和訊息
http://localhost:8084/

# 開啟 Spark Master Web UI 監控作業
http://localhost:8081/
```

#### 5. 停止服務

```bash
# 停止並移除所有容器
docker-compose down
```

---
### 技術說明

- **Kafka**：使用 KRaft 模式（非 ZooKeeper），版本 7.6.0
- **Spark**：使用 Bitnami Spark 3.5 映像檔
- **資料格式**：JSON 格式，包含 strategy, value, ts 欄位
- **處理模式**：Spark Structured Streaming 搭配 Kafka 接口
- **Join 模式**：時間窗口（±5分鐘）內的 Stream-Stream Join

---
### 常見問題排解

1. **Ivy 目錄權限問題**：確保 .ivy2 目錄有正確的權限 `chmod 777 .ivy2`
2. **Kafka 連接問題**：容器內使用 `kafka:29092`，本機使用 `localhost:9092`
3. **Spark 任務失敗**：檢查 Spark UI (http://localhost:8081/) 的日誌 