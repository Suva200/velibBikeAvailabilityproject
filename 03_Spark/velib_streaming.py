#!/usr/bin/env python3

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, sum as spark_sum, expr, last
from pyspark.sql.types import StructType, StructField, IntegerType
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime


# Spark Session
spark = SparkSession.builder \
    .appName("VelibStationStreaming") \
    .getOrCreate()

print("[INFO] Spark session created")

# Kafka & HDFS Settings
kafka_bootstrap = "10.0.0.82:9092,10.0.0.83:9092"
raw_hdfs_path = "hdfs://master:9000/velib/raw"

checkpoint_path_raw = "/tmp/velib_checkpoint_v3_raw"
checkpoint_path_agg = "/tmp/velib_checkpoint_v3_agg"

# JSON Schema 
station_schema = StructType([
    StructField("station_id", IntegerType(), True),
    StructField("num_bikes_available", IntegerType(), True),
    StructField("num_docks_available", IntegerType(), True),
    StructField("is_installed", IntegerType(), True),
    StructField("is_renting", IntegerType(), True),
    StructField("is_returning", IntegerType(), True),
    StructField("last_reported", IntegerType(), True)
])

# Read from Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap) \
    .option("subscribe", "velib-station-status") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

df_string = df.selectExpr("CAST(value AS STRING)")

df_json = df_string \
    .select(from_json(col("value"), station_schema).alias("data")) \
    .select("data.*")

# Write Raw Data to HDFS
df_json.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", raw_hdfs_path) \
    .option("checkpointLocation", checkpoint_path_raw) \
    .start()

# Aggregation 

df_agg = df_json.groupBy("station_id").agg(
    spark_sum("num_bikes_available").alias("total_bikes"),
    spark_sum("num_docks_available").alias("total_docks"),
    last("is_renting").alias("is_renting"),
    last("is_returning").alias("is_returning"),
    last("is_installed").alias("is_installed"),
    last("last_reported").alias("last_reported")
).withColumn(
    "occupancy_pct",
    expr("total_bikes / (total_bikes + total_docks) * 100")
)

# InfluxDB Settings
client = InfluxDBClient(
    url="http://localhost:8086",
    token="WqwyQzggcRkzVXq7A5hou-MH4JsA4yNXFvlSLPHTylHBBGsb0C4BUk7o2A9kRtO1NyZazU3DrxQNVWsAo0kdog==",
    org="esilv"
)

write_api = client.write_api(write_options=SYNCHRONOUS)

# Write to InfluxDB 
def write_to_influx(batch_df, batch_id):
    print(f"[INFO] Processing batch {batch_id}, {batch_df.count()} rows")

    for row in batch_df.collect():
        # Skip rows with None last_reported
        if row.last_reported is None:
            print(f"[WARN] Skipping station_id {row.station_id} due to missing last_reported")
            continue

        ts = datetime.utcfromtimestamp(row.last_reported)

        point = (
            Point("velib_station")
            .tag("station_id", str(row.station_id))
            .field("total_bikes", int(row.total_bikes))
            .field("total_docks", int(row.total_docks))
            .field("occupancy_pct", float(row.occupancy_pct))
            .field("is_renting", int(row.is_renting))
            .field("is_returning", int(row.is_returning))
            .field("is_installed", int(row.is_installed))
            .time(ts, WritePrecision.NS)
        )

        write_api.write(bucket="velib", org="esilv", record=point)

# Start Aggregated Stream
df_agg.writeStream \
    .outputMode("complete") \
    .foreachBatch(write_to_influx) \
    .option("checkpointLocation", checkpoint_path_agg) \
    .start()

# Await termination
spark.streams.awaitAnyTermination()
