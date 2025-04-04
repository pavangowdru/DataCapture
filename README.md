# DataCapture
Capturing changes in SQL database using debezium and pushing it to kafka.
![image](https://github.com/user-attachments/assets/99b35f44-abc0-448a-9b5b-b2d090bf3676)

# Step by step Explaination
1. **WAL (Write-Ahead Log) Captures All Changes**  
   - PostgreSQL logs **INSERT, UPDATE, DELETE** operations in WAL files.
   - WAL is a continuous log of database changes.

2. **pgoutput Plugin Reads the WAL**  
   - The `pgoutput` plugin **extracts** changes from the WAL log.
   - It **filters** and structures the changes in a way that can be sent to subscribers.

3. **Replication Slot Holds Unprocessed Changes**  
   - The **replication slot** (`debezium_slot`) ensures **WAL logs are retained** until Debezium reads them.
   - Without a slot, **WAL logs get deleted**, and Debezium might miss changes.

4. **Debezium Reads from the Slot**  
   - Debezium **connects to the slot** and reads changes **continuously**.
   - It **publishes** the changes to Kafka (or another target system).
   - Once **Debezium reads the data**, PostgreSQL **marks those WAL segments as processed** and can delete them.

### **🛠 Example: How Data Flows**
```
PostgreSQL → WAL → pgoutput → Replication Slot (debezium_slot) → Debezium → Kafka
```

# Logs the entire row before any UPDATE or DELETE.
ALTER TABLE transactions_copy REPLICA IDENTITY FULL;

# Issue	Cause	Fix
No replication slot	PostgreSQL issue	Run pg_create_logical_replication_slot()
Slot exists but no WAL activity	PostgreSQL issue	Check pg_stat_replication and enable logical replication
Debezium not running	Debezium issue	Restart connector and check logs
Debezium running but no Kafka topic	Debezium issue	Check logs for errors and verify topic prefix
Kafka topic missing	Kafka issue	Create the topic manually and check Kafka logs


