import json
import os
import sys
import time
from datetime import datetime
from multiprocessing import Lock

from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError
from kafka.structs import OffsetAndMetadata
from elasticsearch import Elasticsearch
from flask import current_app
from app.models import db
from app.models.log_entry import LogEntry
from app.alert_generator import process_log_entry, initialize_alert_generator

class LogProcessorSingleton:
    _instance = None
    _lock = Lock()
    _initialized = False
    _consumer = None
    _es = None
    _app = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    print("Creating new Log Processor Singleton!", file=sys.stderr)
                    cls._instance = super(LogProcessorSingleton, cls).__new__(cls)
                    try:
                        cls._instance._initialize()
                        cls._initialized = True
                    except Exception as e:
                        print(f"Error initializing Log Processor Singleton: {e}", file=sys.stderr)
                        cls._instance = None
        return cls._instance

    def _initialize(self):
        """Initialize the singleton instance."""
        if self._initialized:
            return

        try:
            # Get Flask app
            from app import create_app
            if not self._app:
                self._app = create_app()

            # Initialize Elasticsearch
            if not self._es:
                self._es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])
                info = self._es.cat.count()
                response = self._es.indices.create(index='our_logs', ignore=400)  # Ignore 400 error if index already exists
                print("index created response: " + str(response), file=sys.stderr)

            # Initialize Kafka consumer
            kafka_broker = os.getenv('KAFKA_BROKER', 'kafka:9092')
            if not self._consumer:
                self._consumer = KafkaConsumer(
                    bootstrap_servers=kafka_broker,
                    group_id='log-consumer-group',
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    auto_commit_interval_ms=1000,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=3000,
                    max_poll_interval_ms=300000,
                    max_poll_records=100
                )

                # Subscribe to the logs topic
                self._consumer.subscribe(['logs'])
                print("Kafka consumer initialized and subscribed to 'logs' topic", file=sys.stderr)

            print("Log Processor Singleton initialized", file=sys.stderr)
            
            # Initialize alert generator
            try:
                initialize_alert_generator()
                print("Alert Generator initialized", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Failed to initialize Alert Generator: {e}", file=sys.stderr)
            
            return True
        except Exception as e:
            print(f"Error in _initialize: {e}", file=sys.stderr)
            raise e

    def __store_log(self, log_entry):
        """Store a log entry in both Elasticsearch and PostgreSQL."""
        # Store in Elasticsearch
        try:
            # Convert datetime objects to ISO format strings for Elasticsearch
            es_log_entry = log_entry.copy()
            if isinstance(es_log_entry.get('timestamp'), datetime):
                es_log_entry['timestamp'] = es_log_entry['timestamp'].isoformat()

            response = self._es.index(index='our_logs', document=es_log_entry)
            print('save log to index: ' + json.dumps(es_log_entry), file=sys.stderr)
        except Exception as e:
            print(f"Error saving to Elasticsearch: {str(e)}", file=sys.stderr)
            # Continue execution to try PostgreSQL

        # Store in PostgreSQL
        try:
            # Convert timestamp string to datetime if needed
            timestamp = log_entry.get('timestamp')
            if isinstance(timestamp, str):
                if timestamp.lower() == 'now()':
                    timestamp = datetime.utcnow()
                else:
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except ValueError:
                        print(f"Invalid timestamp format: {timestamp}, using current time", file=sys.stderr)
                        timestamp = datetime.utcnow()

            # Create LogEntry object
            if not self._app:
                from app import create_app
                self._app = create_app()

            with self._app.app_context():
                try:
                    db_log = LogEntry(
                        timestamp=timestamp,
                        user_id=log_entry.get('user_ID'),
                        event_type=log_entry.get('event_type'),
                        ip_address=log_entry.get('ip_address'),
                        severity=log_entry.get('severity', 'low'),
                        user_agent=log_entry.get('user_agent'),
                        latitude=log_entry.get('geo', [None, None])[0],
                        longitude=log_entry.get('geo', [None, None])[1],
                        additional_data=log_entry.get('additional_data')
                    )
                    
                    # Add and commit to database
                    db.session.add(db_log)
                    db.session.commit()
                    print('Saved log to PostgreSQL database', file=sys.stderr)
                    return True
                except Exception as e:
                    print(f"Error creating or saving LogEntry: {str(e)}", file=sys.stderr)
                    db.session.rollback()
                    return False
        except Exception as e:
            print(f"Error in PostgreSQL storage: {str(e)}", file=sys.stderr)
            if 'db' in locals() and hasattr(db, 'session'):
                db.session.rollback()
            return False

    def consume_log(self):
        """Consume and process a batch of messages."""
        if not self._consumer:
            print("Kafka consumer not initialized", file=sys.stderr)
            return False

        try:
            # Poll for messages
            message_batch = self._consumer.poll(timeout_ms=1000, max_records=100)
            
            if not message_batch:
                print("No messages available", file=sys.stderr)
                return False

            success = False
            for tp, messages in message_batch.items():
                for message in messages:
                    try:
                        print(f"Processing message from topic: {tp.topic}, partition: {tp.partition}, offset: {message.offset}", file=sys.stderr)
                        print(f"Message value: {message.value}", file=sys.stderr)
                        
                        # Parse timestamp if it's a string
                        log_data = message.value
                        if isinstance(log_data.get('timestamp'), str):
                            try:
                                # Try parsing as ISO format first
                                log_data['timestamp'] = datetime.fromisoformat(log_data['timestamp'].replace('Z', '+00:00'))
                            except ValueError:
                                # If that fails, assume it's a PostgreSQL NOW() string and use current time
                                log_data['timestamp'] = datetime.utcnow()
                        
                        if self.__store_log(log_data):
                            success = True
                            
                            # Process log entry for alert generation
                            try:
                                process_log_entry(log_data)
                            except Exception as e:
                                print(f"Warning: Failed to process log for alerts: {e}", file=sys.stderr)
                            
                            # Commit offset for successful message
                            self._consumer.commit({tp: OffsetAndMetadata(message.offset + 1, None)})
                    except Exception as e:
                        print(f"Error processing message: {str(e)}", file=sys.stderr)
                        print(f"Message content: {message.value}", file=sys.stderr)
                        print(f"Stack trace:", file=sys.stderr)
                        import traceback
                        traceback.print_exc(file=sys.stderr)
                        continue

            return success
        except KafkaError as e:
            print(f"Kafka error: {str(e)}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Unexpected error in consume_log: {str(e)}", file=sys.stderr)
            print(f"Stack trace:", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return False

# kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic logs --from-beginning
# kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic logs --from-beginning
# curl -X GET 'http://localhost:9200/our_logs/_search'