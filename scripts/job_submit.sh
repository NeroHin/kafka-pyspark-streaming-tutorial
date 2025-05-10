#!/usr/bin/env bash
###############################################################################
# job_submit.sh —— 提交 PySpark Job 到 Spark 叢集
###############################################################################
set -euo pipefail

# === 可自行調整的變數 ========================================================
SPARK_MASTER_CONTAINER=${SPARK_MASTER_CONTAINER:-spark-master}
SPARK_MASTER_URL=${SPARK_MASTER_URL:-spark://spark-master:7077}
KAFKA_PACKAGE="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"

# === 參數檢查 ================================================================
if [[ $# -lt 1 ]]; then
  echo "❌  用法: $0 <PySpark 檔案> [spark-submit 其他參數]"
  exit 1
fi
APP_FILE=$1
shift || true             # 將 $APP_FILE 移除，其餘參數傳遞給 spark-submit

# === 判斷是否在互動終端機 =====================================================
DOCKER_FLAGS="-i"         # 預設只保留 -i（標準輸入）
if [[ -t 0 ]]; then       # 若腳本本身就在 TTY 中執行，再加上 -t
  DOCKER_FLAGS="-it"
fi

# === 執行 spark-submit =======================================================
docker exec $DOCKER_FLAGS "$SPARK_MASTER_CONTAINER" bash -c "
  JAVA_HOME=/opt/bitnami/java \
  spark-submit \
    --master $SPARK_MASTER_URL \
    --packages $KAFKA_PACKAGE \
    --conf spark.jars.ivy=/opt/bitnami/ivy \
    --conf spark.cores.max=1 \
    --conf spark.executor.instances=1 \
    --conf spark.executor.cores=1 \
    --conf spark.executor.memory=1g \
    --conf spark.dynamicAllocation.enabled=false \
    /opt/bitnami/spark/scripts/$APP_FILE $*
"