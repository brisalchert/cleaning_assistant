import io
import psycopg
from abc import ABC, abstractmethod
from pandas import DataFrame


class DatabaseAccess(ABC):
    @property
    @abstractmethod
    def data_file(self) -> io.TextIOWrapper:
        """Abstract attribute for data file"""
        pass

    @abstractmethod
    def set_connection_details(self, database: str, user: str, host: str, password: str, port: int = 5432):
        """Abstract method for creating a connection to an external Postgres database"""
        pass

    @abstractmethod
    def set_engine(self):
        """Abstract method for creating a connection engine to an external Postgres database"""
        pass

    @abstractmethod
    def set_file(self, file_path: str):
        """Abstract method for setting the file path for the CSV file to be cleaned"""
        pass

    @abstractmethod
    def close_file(self):
        """Abstract method for closing the CSV file"""
        pass

    @abstractmethod
    def get_tables(self) -> dict[str, DataFrame]:
        """Abstract method for getting a list of database tables as DataFrames"""
        pass
