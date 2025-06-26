import os
import sys
import json
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

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

        # Create an admin client
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=kafka_broker)

            # Define the topic
            topic_name = 'logs'
            num_partitions = 1
            replication_factor = 1

            # Create the topic if it doesn't exist
            try:
                topic_list = [NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
                admin_client.create_topics(new_topics=topic_list)
                print(f'Topic "{topic_name}" was created', file=sys.stderr)
            except TopicAlreadyExistsError:
                print(f'Topic "{topic_name}" already exists, skip', file=sys.stderr)
            except Exception as e:
                print(f'Error creating topic: {e}', file=sys.stderr)
            finally:
                admin_client.close()
        except Exception as e:
            print(f'Error with admin client: {e}', file=sys.stderr)

        # Create a Kafka producer instance
        self.__producer = KafkaProducer(
            bootstrap_servers=kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka producer initialized", file=sys.stderr)

    def produce_log(self, log_data):
        """ Function to produce logs to the 'logs' topic """
        try:
            future = self.__producer.send('logs', value=log_data)
            # Wait for the message to be delivered
            record_metadata = future.get(timeout=10)
            print(f'Message delivered to partition {record_metadata.partition} at offset {record_metadata.offset}', file=sys.stderr)
            print('produce data: ' + json.dumps(log_data), file=sys.stderr)
            return True
        except Exception as e:
            print(f'Failed to produce log: {e}', file=sys.stderr)
            return False
