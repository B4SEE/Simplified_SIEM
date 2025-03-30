import os
import sys
from time import sleep

from confluent_kafka import Producer
from kafka.admin import KafkaAdminClient, NewTopic
import json


# Ensure the KAFKA_BROKER environment variable is set
kafka_broker = os.getenv('KAFKA_BROKER', 'kafka:9092')
if not kafka_broker:
    raise EnvironmentError("KAFKA_BROKER environment variable is not set")

# Kafka configuration
conf = {
    'bootstrap.servers': 'kafka:9092',  # Use the KAFKA_BROKER environment variable
}

# Create an admin client
admin_client = KafkaAdminClient(
    bootstrap_servers='kafka:9092',
    client_id='log_topic_creator'
)

# Define the topic
topic_name = 'logs'
num_partitions = 1
replication_factor = 1

# Check if the topic already exists
existing_topics = admin_client.list_topics()
if topic_name not in existing_topics:
    # Create the topic
    topic_list = [NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
else:
    print(f'Topic "{topic_name}" already exists, skip', file=sys.stderr)


# Create a Kafka producer instance
producer = Producer(conf)

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Delivery failed for message: {err}', file=sys.stderr)
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]', file=sys.stderr)


def produce_log(log_data):
    """ Function to produce logs to the 'logs' topic """
    try:
        # Produce the log message to the 'logs' topic
        producer.produce('logs', value=json.dumps(log_data), callback=delivery_report)
        # Wait up to 1 second for events. Callbacks will be invoked during
        # this method call if the message is acknowledged.
        producer.poll(1)
        print('produce data: ' + json.dumps(log_data), file=sys.stderr)
        return True
    except Exception as e:
        print(f'Failed to produce log: {e}', file=sys.stderr)
        return False