import os
import json
import zlib
import logging
from confluent_kafka import Consumer

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger('demo-consumer')

# Configuration
broker = os.getenv('KAFKA_BROKER', 'kafka:9093')
topic  = os.getenv('KAFKA_TOPIC', 'demo-topic')

# Kafka consumer settings
conf = {
    'bootstrap.servers': broker,
    'group.id':          'demo-group',
    'auto.offset.reset': 'earliest',
}
consumer = Consumer(conf)
consumer.subscribe([topic])

def consume_loop():
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error(f"Consumer error: {msg.error()}")
            continue

        # Entire batch arrives as compressed bytes
        compressed = msg.value()
        try:
            # decompress back to newline-delimited JSON
            payload = zlib.decompress(compressed)
        except zlib.error as e:
            logger.error(f"Decompression failed: {e}")
            continue

        # split into individual JSON records
        for line in payload.split(b'\n'):
            try:
                obj = json.loads(line.decode('utf-8'))
                logger.info(f"Received: {obj}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")

if __name__ == '__main__':
    try:
        consume_loop()
    except KeyboardInterrupt:
        print("Consumer shutting down…")
    finally:
        consumer.close()
