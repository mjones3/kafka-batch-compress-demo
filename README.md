# kafka-batch-compress-demo

A reference implementation of an efficient, high-throughput streaming pipeline using Apache Kafka, Docker Compose, and message-level compression.

## What This Project Does

- **Generates JSON records** in a Python producer, simulating high-volume event streams.  
- **Batches** hundreds of small JSON messages into a single payload to reduce per-message overhead.  
- **Compresses** each batch (using zlib or broker-side LZ4) to shrink data size on the wire.  
- **Publishes** compressed batches to a Kafka topic.  
- **Consumes** batches in a Python consumer, **decompresses**, splits them back into individual JSON records, and logs them.

## Why Compression & Batching Matter

1. **Reduced Network Overhead**  
   - Each Kafka message incurs TCP framing, protocol headers, and broker metadata. Batching hundreds of records into one reduces this overhead by up to 100×.

2. **Improved Bandwidth Utilization**  
   - Compressing redundant JSON strings (field names, structure) can cut payload sizes by 70–90%, saving cloud egress costs and speeding delivery.

3. **Better Throughput & Scalability**  
   - Fewer, larger messages allow Kafka to optimize disk I/O and replication, resulting in higher sustained message rates and lower cluster load.

4. **Low Latency with Tunable Trade-Offs**  
   - By adjusting linger times and batch limits, you can balance end-to-end latency against bandwidth and throughput gains.

## Real-World Use Cases

- **IoT Telemetry**: Sensor networks emitting frequent small readings (temperature, GPS) benefit from batching + compression to minimize connectivity costs.  
- **Financial Market Data**: High-frequency tick streams can be compressed to reduce latency and improve real-time analytics.  
- **Healthcare Monitoring**: Continuous vitals (ECG, blood pressure) require encrypted—and optionally compressed—transport to cloud analytics.  
- **Log Aggregation**: Microservices logging JSON events can batch and compress logs before sending to central pipelines (Kafka → ELK/Splunk).

---

## Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/mjones3/kafka-batch-compress-demo.git
   cd kafka-batch-compress-demo
2. **Start the stack**  
   ```bash
   docker-compose up -d
3. **View Logs**
    ```bash
    docker-compose logs -f producer consumer
4. **Shut Down**
    ```bash
    docker-compose down


***Docker Compose Environment Variables***
### kafka

- **KAFKA_LISTENERS**  
  Defines two listeners:  
  - `INSIDE://0.0.0.0:9093` (internal traffic)  
  - `OUTSIDE://0.0.0.0:9094` (external access)

- **KAFKA_ADVERTISED_LISTENERS**  
  Informs clients to reach the broker at `kafka:9093` internally and `localhost:9094` externally.

- **KAFKA_LISTENER_SECURITY_PROTOCOL_MAP**  
  Maps both listeners to `PLAINTEXT` (no TLS).

- **KAFKA_INTER_BROKER_LISTENER_NAME**  
  Uses the `INSIDE` listener for replication and metadata.

- **KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1**  
  Single replica for `__consumer_offsets` (dev-friendly).

- **KAFKA_AUTO_CREATE_TOPICS_ENABLE=true**  
  Automatically creates topics like `demo-topic`.

---

### producer

- **KAFKA_BROKER=kafka:9093**  
  Address where the producer sends batches.

- **KAFKA_TOPIC=demo-topic**  
  The topic for compressed payloads.

- **(Optional) COMPRESSION_CODEC**  
  e.g. `lz4` to enable broker-side compression.

---

### consumer

- **KAFKA_BROKER=kafka:9093**  
  Address for consuming compressed batches.

- **KAFKA_TOPIC=demo-topic**  
  Same topic the producer writes to.
