import io
import psycopg
from pandas import DataFrame, Series
from model import DataModel
from services.AbstractService import AbstractService
from services.DatabaseAccess import DatabaseAccess
from services.ModelEditor import ModelEditor


class DatabaseService(AbstractService, DatabaseAccess, ModelEditor):
    @property
    def db_connection(self) -> psycopg.Connection:
        return self._db_connection

    @property
    def data_file(self) -> io.TextIOWrapper:
        return self._data_file

    @property
    def model(self) -> DataModel:
        return self._model

    def __init__(self, model: DataModel):
        self._model = model
        self._db_connection = None
        self._data_file = None

    # --- DatabaseAccess overrides ---

    def set_connection(self, database: str, user: str, host: str, password: str, port: int = 5432):
        self._db_connection = psycopg.connect(database=database, user=user, host=host, password=password, port=port)

    def close_connection(self):
        self._db_connection.close()

    def set_file(self, file_path: str):
        self._data_file = open(file_path, "r")

    def close_file(self):
        self._data_file.close()

    def get_tables(self) -> dict[str, DataFrame]:
        # TODO: Implement get_tables
        pass

    # --- ModelEditor overrides ---

    def create_row(self, table_name: str, columns: dict) -> bool:
        return self._model.create_row(table_name, columns)

    def read_row(self, table_name: str, primary_key: str) -> Series:
        return self._model.read_row(table_name, primary_key)

    def update_row(self, table_name: str, primary_key: str, columns: dict) -> bool:
        return self._model.update_row(table_name, primary_key, columns)

    def delete_row(self, table_name: str, primary_key: str) -> Series:
        return self._model.delete_row(table_name, primary_key)

    # --- Subclass methods ---

    def load_from_database(self) -> bool:
        # TODO: Implement load_from_database
        pass

    def load_from_file(self) -> bool:
        # TODO: Implement load_from_file
        pass

    def reset_data(self):
        # TODO: Implement reset_data
        pass
