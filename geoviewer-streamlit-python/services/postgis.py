import leafmap
import pandas as pd


class PostGISConnection:
    _instance = None

    def __new__(
        cls, database, host="localhost", user="postgres", password="", port=5432
    ):
        if cls._instance is None:
            cls._instance = super(PostGISConnection, cls).__new__(cls)
            cls._instance.database = database
            cls._instance.host = host
            cls._instance.user = user
            cls._instance.password = password
            cls._instance.port = port
            cls._instance.engine = None
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        try:
            self.engine = leafmap.connect_postgis(
                database=self.database,
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
            )
            print("PostGIS connection established successfully.")
        except Exception as e:
            print(f"Failed to connect to PostGIS: {e}")

    def get_connection(self):
        return self.engine


class PostGISHandler:

    def __init__(self, connection: PostGISConnection):
        self.engine = connection.get_connection()

    def execute_query(self, query, geom_col=None):
        try:
            if geom_col:
                df = leafmap.read_postgis(query, self.engine, geom_col=geom_col)
            else:
                df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            print(f"Query execution failed: {e}")
            return None
