import os
from confluent_kafka import Producer
import json

# Ensure the KAFKA_BROKER environment variable is set
kafka_broker = os.getenv('KAFKA_BROKER')
if not kafka_broker:
    raise EnvironmentError("KAFKA_BROKER environment variable is not set")

# Kafka configuration
conf = {
    'bootstrap.servers': 'kafka:9092',  # Use the KAFKA_BROKER environment variable
}

# Create a Kafka producer instance
producer = Producer(conf)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Delivery failed for message: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def produce_log(log_data):
    """ Function to produce logs to the 'logs' topic """
    try:
        print(log_data)
        # Produce the log message to the 'logs' topic
        producer.produce('logs', value=json.dumps(log_data), callback=delivery_report)
        # Wait up to 1 second for events. Callbacks will be invoked during
        # this method call if the message is acknowledged.
        producer.poll(1)
        return True
    except Exception as e:
        print(f'Failed to produce log: {e}')
        return False