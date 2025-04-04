from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, LongType

# Create Spark Session
spark = SparkSession.builder \
    .appName("KafkaSparkElasticsearch") \
    .config("spark.es.nodes", "elasticsearch") \
    .config("spark.es.port", "9200") \
    .config("spark.es.nodes.wan.only", "true") \
    .getOrCreate()

# Define Schema
#schema = StructType().add("user", StringType()).add("message", StringType())

print("------Read from Kafka------------")

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:29092") \
    .option("subscribe", "cdc.public.transactions_copy") \
    .load()

schema = StructType().add(
    "payload",
    StructType().add(
        "after",
        StructType([
            StructField("transaction_id", StringType(), nullable=False),
            StructField("user_id", StringType(), nullable=True),
            StructField("modified_by", StringType(), nullable=True),
            StructField("modified_at", LongType(), nullable=True),  # MicroTimestamp is int64
            StructField("change_info", StringType(), nullable=True)  # Json is treated as String
        ])
    )
)

print("------Printing Schema------------")

df.printSchema()    

df = df.select(from_json(col("value").cast("string"), schema).alias("data"))
df = df.select("data.payload.after.*")

# 👇 Just for testing, write to console instead of ES
print("------Writing data to console------------")
# df.writeStream \
#   .format("console") \
#   .start() \
#   .awaitTermination()

# Transform Data
#df = df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), schema).alias("data")).select("data.*")

# Write to Elasticsearch
print("------Writing data to Elasticsearch------------")
# Write to Elasticsearch
query = df.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("checkpointLocation", "/tmp/spark-checkpoints") \
    .option("es.resource", "kafka-data") \
    .option("es.nodes.wan.only", "true") \
    .outputMode("append") \
    .start()

spark.streams.awaitAnyTermination()
