import json
import os
import sys
import time

from kafka import KafkaConsumer
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
        self.consumer = KafkaConsumer(
            'logs',
            bootstrap_servers=kafka_broker,
            group_id='log-consumer-group',
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        # Elasticsearch configuration
        self.__es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])
        info = self.__es.cat.count()
        response = self.__es.indices.create(index='our_logs', ignore=400)  # Ignore 400 error if index already exists

        print("index created response: " + str(response), file=sys.stderr)
        print("Log Processor Singleton initialized", file=sys.stderr)

    def __store_log(self, log_entry):
        response = self.__es.index(index='our_logs', document=log_entry)
        print('save log to index: ' + json.dumps(log_entry), file=sys.stderr)

    def consume_log(self):
        # Get the next message from the consumer
        try:
            for message in self.consumer:
                print(f"Topic: {message.topic}, Partition: {message.partition}, Offset: {message.offset}", file=sys.stderr)
                print(f"Key: {message.key}, Value: {message.value}, Type: {type(message.value)}", file=sys.stderr)
                
                log_entry = message.value  # Value is already deserialized
                print(f"Log entry: {log_entry}", file=sys.stderr)
                
                self.__store_log(log_entry)
                break  # Only process one message at a time
        except Exception as e:
            print(f"Error consuming message: {e}", file=sys.stderr)
            return

# kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic logs --from-beginning
# kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic logs --from-beginning
# curl -X GET 'http://localhost:9200/our_logs/_search'