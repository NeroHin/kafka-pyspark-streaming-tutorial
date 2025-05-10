#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USAGE
-----
spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  merge_c_d.py
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, from_json, greatest, to_json, to_timestamp, struct
from pyspark.sql.types import StructType, StructField, IntegerType, LongType

# --------------------------------------------------
# 1. Spark & Kafka 基本設定
# --------------------------------------------------
KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"  # Set to container internal address

spark = (
    SparkSession.builder
        .appName("Merge_C_and_D")
        .config("spark.sql.session.timeZone", "Asia/Taipei")        # 與 Kafka 產生端一致
        .config("spark.sql.shuffle.partitions", "8")                # 視叢集資源調整
        .getOrCreate()
)

# --------------------------------------------------
# 2. 定義 Kafka 訊息 JSON schema（時間戳皆為毫秒整數）
# --------------------------------------------------
schema_c = StructType([
    StructField("result", IntegerType()),
    StructField("ts",     LongType())          # 毫秒
])

schema_d = StructType([
    StructField("some_value", IntegerType()),
    StructField("ts",        LongType())       # 毫秒
])

# --------------------------------------------------
# 3. 讀取 C_output 與 D_input
# --------------------------------------------------
c_raw = (
    spark.readStream.format("kafka")
         .option("subscribe", "C_output")
         .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
         .load()
)

d_raw = (
    spark.readStream.format("kafka")
         .option("subscribe", "D_input")
         .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
         .load()
)

# --------------------------------------------------
# 4. 解析 JSON、轉換時間欄位並建立 watermark
# --------------------------------------------------
c_parsed = (
    c_raw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) AS json")
         .select("key", from_json("json", schema_c).alias("c"))
         .select(
             col("key"),
             col("c.result").alias("c_val"),
             to_timestamp(col("c.ts") / 1000.0).alias("c_ts")       # 毫秒 → timestamp
         )
         .withWatermark("c_ts", "30 minutes")
         .alias("c")
)

d_parsed = (
    d_raw.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) AS json")
         .select("key", from_json("json", schema_d).alias("d"))
         .select(
             col("key"),
             col("d.some_value").alias("d_val"),
             to_timestamp(col("d.ts") / 1000.0).alias("d_ts")
         )
         .withWatermark("d_ts", "30 minutes")
         .alias("d")
)

# --------------------------------------------------
# 5. 時間區間內 inner join
# --------------------------------------------------
joined = (
    c_parsed.join(
        d_parsed,
        expr("""
            c.key = d.key AND
            d.d_ts BETWEEN c.c_ts - interval 5 minutes AND c.c_ts + interval 5 minutes
        """),
        "inner"
    )
    .select(
        col("c.key").alias("key"),
        to_json(struct(
            col("c_val"),
            col("d_val"),
            greatest(col("c_ts"), col("d_ts")).alias("ts")
        )).alias("value")
    )
)

# --------------------------------------------------
# 6. 輸出至 Kafka topic：D_input_ready
# --------------------------------------------------
query = (
    joined.writeStream
          .format("kafka")
          .option("topic", "D_input_ready")
          .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
          .option("checkpointLocation", "/tmp/ckpt_merge")
          .outputMode("append")
          .start()
)

query.awaitTermination()