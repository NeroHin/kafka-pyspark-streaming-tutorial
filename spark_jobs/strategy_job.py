"""
USAGE:
spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  strategy_job.py --strategies A B C D
"""
import argparse, json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, when, pow
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType

# Kafka setup
KAFKA_BOOTSTRAP_SERVERS = "kafka:29092"  # Set to container internal address

parser = argparse.ArgumentParser()
parser.add_argument("--strategies", nargs='+', required=True, help="List of strategies (e.g., A B C D)")
args = parser.parse_args()
STRATEGIES = [s.upper() for s in args.strategies]

spark = (SparkSession.builder
         .appName(f"Multi-Strategy-{''.join(STRATEGIES)}")
         .getOrCreate())

schema = StructType([
    StructField("strategy", StringType()),
    StructField("value", IntegerType()),
    StructField("ts",    LongType())
])

# Create input topics pattern for subscription
input_topics_pattern = f"({'|'.join(STRATEGIES)})_input"

df = (spark.readStream
      .format("kafka")
      .option("subscribePattern", input_topics_pattern)
      .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
      .load())

# Parse JSON and perform complex calculations
parsed = (df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING) as json")
            .select(col("key"),
                    from_json(col("json"), schema).alias("data"))
            .select(
                col("key"),
                col("data.strategy").alias("strategy"),
                (
                    when(col("data.value") < 30, col("data.value") * 2)
                    .when(col("data.value").between(30, 60), col("data.value") * 1.5 + 10) 
                    .when(col("data.value") > 60, pow(col("data.value"), 2) / 100)
                ).cast("integer").alias("result"),
                col("data.ts").alias("ts")))

# Serialize output
out = parsed.selectExpr(
    "key",
    "strategy",
    "to_json(struct(result, ts)) AS value"
)

# Write to multiple output topics based on strategy
for strategy in STRATEGIES:
    query = (out
             .filter(col("strategy") == strategy)
             .drop("strategy")
             .writeStream
             .format("kafka")
             .option("topic", f"{strategy}_output")
             .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
             .option("checkpointLocation", f"/tmp/ckpt_{strategy}")
             .outputMode("append")
             .start())

# Wait for all queries to terminate
spark.streams.awaitAnyTermination()