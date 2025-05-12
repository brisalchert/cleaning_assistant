import psycopg
from abc import ABC, abstractmethod
from pandas import DataFrame

class DatabaseAccess(ABC):
    @property
    @abstractmethod
    def db_connection(self) -> psycopg.Connection:
        """Abstract attribute for database connection"""
        pass

    @abstractmethod
    def set_connection(self, database: str, user: str, host: str, password: str, port: int = 5432):
        """Abstract method for creating a connection to an external Postgres database"""
        pass

    @abstractmethod
    def close_connection(self):
        """Abstract method for closing the connection to the Postgres database"""
        pass

    @abstractmethod
    def set_file(self, file_path: str):
        """Abstract method for setting the file path for the CSV file to be cleaned"""
        pass

    @abstractmethod
    def get_tables(self) -> dict[str, DataFrame]:
        """Abstract method for getting a list of database tables as DataFrames"""
        pass
