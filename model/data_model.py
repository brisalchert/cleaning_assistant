import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal
from pandas import DataFrame, Series


class DataModel(QObject):
    data_changed: pyqtSignal = pyqtSignal(dict)

    def __init__(self, database: dict[str, DataFrame] = None):
        super().__init__()
        self._database = database
        self._observers = []

    def get_database(self):
        return self._database

    def get_table(self, table_name: str) -> DataFrame:
        return self._database[table_name]

    def set_database(self, database: dict[str, DataFrame]):
        self._database = database
        self.data_changed.emit(database)

    def set_table(self, table_name: str, table: DataFrame):
        self._database[table_name] = table
        self.data_changed.emit(self._database)

    def update_row(self, table_name: str, new_row_df: DataFrame) -> bool:
        # Check for the table in the database
        if table_name not in self._database:
            return False

        # Update the row in the database, or return False if not found
        if not new_row_df.index.difference(self._database[table_name].index).empty:
            return False
        else:
            self._database[table_name].update(new_row_df)
            self.data_changed.emit(self._database)
            return True
