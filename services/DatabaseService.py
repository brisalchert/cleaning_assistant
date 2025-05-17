import io
import pandas as pd
from pandas import DataFrame, Series
from sqlalchemy import create_engine, text, URL
from model import DataModel
from services import AbstractService
from services import DatabaseAccess
from services import ModelEditor


class DatabaseService(AbstractService, DatabaseAccess, ModelEditor):
    @property
    def data_file(self) -> io.TextIOWrapper:
        return self._data_file

    @property
    def model(self) -> DataModel:
        return self._model

    def __init__(self, model: DataModel):
        self.engine = None
        self._model = model
        self._db_connection_details: dict = {}
        self._data_file = None

    # --- DatabaseAccess overrides ---

    def set_connection_details(self, dbname: str, user: str, host: str, password: str, port: int = 5432):
        self._db_connection_details = {
            "dbname": dbname,
            "user": user,
            "host": host,
            "password": password,
            "port": port
        }

    def set_engine(self):
        db_config = self._db_connection_details

        self.engine = create_engine(URL.create(
            drivername="postgresql+psycopg",
            username=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["dbname"]
        ))

    def set_file(self, file_path: str):
        self._data_file = open(file_path, "r")

    def close_file(self):
        self._data_file.close()

    def get_tables(self, schema: str = "public") -> dict[str, DataFrame]:
        # Dictionary for table names
        table_names_dict = {}

        # Establish database connection
        with self.engine.connect() as connection:
            # Get table names from database using SQLAlchemy
            result = connection.execute(text("""
                 SELECT table_name
                 FROM information_schema.tables
                 WHERE table_schema = :schema
                   AND table_type = 'BASE TABLE'
             """), {"schema": schema})

            table_names = [row[0] for row in result]

            # Convert tables to DataFrames
            for table in table_names:
                df = pd.read_sql(f"SELECT * FROM {schema}.{table}", connection)
                table_names_dict[table] = df

        return table_names_dict

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

    def load_from_database(self, connection_details: dict) -> bool:
        # TODO: Add exception handling
        self.set_connection_details(**connection_details)
        self.set_engine()

        tables = self.get_tables()
        self._model.set_database(tables)

        return True

    def load_from_file(self) -> bool:
        # TODO: Implement load_from_file
        pass

    def reset_data(self):
        # TODO: Implement reset_data
        pass
