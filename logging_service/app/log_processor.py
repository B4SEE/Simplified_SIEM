import json
import os
import sys

from flask import jsonify
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch

# Kafka configuration
kafka_broker = os.getenv('KAFKA_BROKER', 'kafka:9092')
conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'log-consumer-group',
    'auto.offset.reset': 'earliest'
}
# consumer = Consumer(conf)

consumer = KafkaConsumer(
 bootstrap_servers = 'kafka:9092',
)

consumer.subscribe(['logs'])

print(consumer.topics(), file=sys.stderr)
print(consumer.subscription(), file=sys.stderr)


es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])

es.indices.create(index='our_logs', ignore=400)  # Ignore 400 error if index already exists




def consume_log():
    msg = consumer.poll(10)
    if msg is None:
        print("No message received", file=sys.stderr)
        return
    print(msg, file=sys.stderr)
    for tp, records in msg.items():
        for record in records:
            print(f"Topic: {record.topic}, Partition: {record.partition}, Offset: {record.offset}", file=sys.stderr)
            print(f"Key: {record.key}, Value: {record.value}", file=sys.stderr)
            log_entry = json.loads(record.value.decode('utf-8'))
            store_log(log_entry)

def store_log(log_entry):
    es.index(index='our_logs', body=log_entry, headers={"Content-Type": "application/json"})
    print('save log to index: ' + json.dumps(log_entry), file=sys.stderr)

# kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic logs --from-beginning