from abc import ABC, abstractmethod

from pandas import DataFrame


class DatabaseAccess(ABC):
    @property
    @abstractmethod
    def data_files(self):
        """Abstract attribute for data files"""
        pass

    @data_files.setter
    @abstractmethod
    def data_files(self, data):
        """Abstract setter for data files"""
        pass

    @abstractmethod
    def _set_connection_details(self, database: str, user: str, host: str, password: str, port: int = 5432):
        """Abstract method for creating a connection to an external Postgres database"""
        pass

    @abstractmethod
    def _set_engine(self):
        """Abstract method for creating a connection engine to an external Postgres database"""
        pass

    @abstractmethod
    def _load_tables_database(self) -> dict[str, DataFrame]:
        """Abstract method for getting a list of database tables as DataFrames"""
        pass

    @abstractmethod
    def _load_table_file(self, file_path: str, csv_config: dict) -> DataFrame:
        """Abstract method for getting a database table as a DataFrame from a CSV file"""
        pass
