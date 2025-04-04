#!/bin/bash
docker cp ./stream_kafka_to_es.py spark-master:/opt/bitnami/spark/

# Following command is not running
# the path "/opt/bitnami/spark/stream_kafka_to_es.py" is referring to windows path instead of path inside container
docker exec -it spark-master spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.7.0 \
  /opt/bitnami/spark/stream_kafka_to_es.py
  
  