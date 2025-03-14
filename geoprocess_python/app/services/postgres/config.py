from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()

class DBConnectionHandler:
    """
    SQLAlchemy database connection.
    """

    def __init__(self) -> None:
        self.__connection_string = os.getenv("POSTGIS_CONNECTIION_STRING")
        self.session = None

    def get_engine(self):
        engine = create_engine(self.__connection_string)
        return engine

    def __enter__(self):
        engine = create_engine(self.__connection_string)
        session_maker = sessionmaker()
        self.session = session_maker(bind=engine)
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self.session.close()