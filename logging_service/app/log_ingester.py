import os
import sys
import json
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic

class KafkaProducerSingleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(KafkaProducerSingleton, cls).__new__(cls)
            try:
                cls.__instance.__initialize()
            except Exception as e:
                print(f"Error initializing Kafka producer: {e}", file=sys.stderr)
                cls.__instance = None
        return cls.__instance

    def __initialize(self):
        # Ensure the KAFKA_BROKER environment variable is set
        kafka_broker = os.getenv('KAFKA_BROKER', 'kafka:9092')
        if not kafka_broker:
            raise EnvironmentError("KAFKA_BROKER environment variable is not set")

        # Kafka configuration
        conf = {'bootstrap.servers': kafka_broker}

        # Create an admin client
        admin_client = AdminClient({'bootstrap.servers': kafka_broker})

        # Define the topic
        topic_name = 'logs'
        num_partitions = 1
        replication_factor = 1

        # Check if the topic already exists
        existing_topics = admin_client.list_topics().topics
        print(f'Existing topics: {existing_topics}', file=sys.stderr)
        if topic_name not in existing_topics:
            # Create the topic
            topic_list = [NewTopic(topic=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print(f'Topic "{topic_name}" was created', file=sys.stderr)
        else:
            print(f'Topic "{topic_name}" already exists, skip', file=sys.stderr)

        # Create a Kafka producer instance
        self.__producer = Producer(conf)
        print("Kafka producer initialized", file=sys.stderr)

    def __produce(self, topic, value, callback):
        self.__producer.produce(topic, value=value, callback=callback)
        self.__producer.flush()


    def produce_log(self, log_data):
        """ Function to produce logs to the 'logs' topic """
        try:
            self.__produce('logs', value=json.dumps(log_data), callback=delivery_report)
            print('produce data: ' + json.dumps(log_data), file=sys.stderr)
            return True
        except Exception as e:
            print(f'Failed to produce log: {e}', file=sys.stderr)
            return False

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Delivery failed for message: {err}', file=sys.stderr)
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]', file=sys.stderr)
