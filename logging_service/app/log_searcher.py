import sys

from elasticsearch import Elasticsearch

class LogSearcherSingleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            print("There is no Searcher Singleton!", file=sys.stderr)
            cls.__instance = super(LogSearcherSingleton, cls).__new__(cls)
            try:
                cls.__instance.__initialize()
            except Exception as e:
                print(f"Error initializing Log Searcher Singleton: {e}", file=sys.stderr)
                cls.__instance = None
        return cls.__instance

    def __initialize(self):
        # Elasticsearch configuration
        self.__es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'}])
        info = self.__es.info()
        print("Log Searcher Singleton initialized: " + info.body, file=sys.stderr)
