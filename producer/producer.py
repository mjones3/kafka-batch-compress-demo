import os
import json
import time
import random
import string
import zlib
from confluent_kafka import Producer

# Configuration
broker = os.getenv('KAFKA_BROKER', 'kafka:9093')
topic  = os.getenv('KAFKA_TOPIC', 'demo-topic')

# Kafka producer settings
conf = {
    'bootstrap.servers': broker,
    'linger.ms': 100,
    'batch.num.messages': 500,
     # broker‐side compression:
    'compression.codec': 'lz4'
}
producer = Producer(conf)

def produce_loop():
    batch       = []
    batch_limit = 100

    while True:
        # 1) create a random JSON record
        record = {
            'id':    random.randint(1, 100_000),
            'value': random.random(),
            'name':  ''.join(random.choices(string.ascii_letters, k=5))
        }

        # 2) append JSON text
        batch.append(json.dumps(record))

        # 3) once we've collected batch_limit records, compress & send
        if len(batch) >= batch_limit:
            # join with newline, encode to bytes
            payload = '\n'.join(batch).encode('utf-8')
            # compress with zlib (default compression level)
            compressed = zlib.compress(payload)

            # produce compressed blob
            producer.produce(topic, compressed)
            # serve delivery callbacks so the local queue doesn't fill
            producer.poll(0)
            print(f"Sent batch of {len(batch)} messages ({len(compressed)} bytes compressed)")

            # clear for next batch
            batch.clear()

        # throttle generation so we don't spin too fast
        time.sleep(0.01)

if __name__ == '__main__':
    try:
        produce_loop()
    except KeyboardInterrupt:
        print("Producer shutting down…")
        producer.flush()
