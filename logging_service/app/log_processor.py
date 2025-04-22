import json
import os
import sys
import time

from confluent_kafka import Consumer
from elasticsearch import Elasticsearch

class LogProcessorSingleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            print("There is no Processor Singleton!", file=sys.stderr)
            cls.__instance = super(LogProcessorSingleton, cls).__new__(cls)
            try:
                cls.__instance.__initialize()
            except Exception as e:
                print(f"Error initializing Log Processor Singleton: {e}", file=sys.stderr)
                cls.__instance = None
        return cls.__instance

    def __initialize(self):
        # Kafka configuration
        kafka_broker = os.getenv('KAFKA_BROKER', 'kafka:9092')
        self.consumer_conf = {
            'bootstrap.servers': kafka_broker,
            'group.id': 'log-consumer-group',
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(self.consumer_conf)
        self.consumer = Consumer(self.consumer_conf)
        self.consumer.subscribe(['logs'])

        # Elasticsearch configuration
        self.__es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])
        # self.__es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])
        info = self.__es.cat.count()
        response = self.__es.indices.create(index='our_logs', ignore=400)  # Ignore 400 error if index already exists

        print("index created response: " + str(response), file=sys.stderr)

        print("Log Processor Singleton initialized", file=sys.stderr)

    def __store_log(self, log_entry):

        response = self.__es.index(index='our_logs', document=log_entry)
        print('save log to index: ' + json.dumps(log_entry), file=sys.stderr)

    def consume_log(self):

        msg = self.consumer.poll(1.0)
        if msg is None:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No message received", file=sys.stderr)
            return
        if msg.error():
            print(f"Error: {msg.error()}", file=sys.stderr)
            return

        print(f"Topic: {msg.topic()}, Partition: {msg.partition()}, Offset: {msg.offset()}", file=sys.stderr)
        print(f"Key: {msg.key()}, Value: {msg.value()}, Type: {type(msg.value())}", file=sys.stderr)
        # log_entry = json.loads(msg.value)
        log_entry = json.loads(msg.value())
        print(f"Log entry: {log_entry}", file=sys.stderr)

        self.__store_log(log_entry)


# kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic logs --from-beginning
# kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic logs --from-beginning
# curl -X GET 'http://localhost:9200/our_logs/_search'