import pandas as pd
from pandas import DataFrame, Series


class DataModel:
    def __init__(self, database: dict[str, DataFrame] = None):
        self._database = database
        self._observers = []

    def get_database(self):
        return self._database

    def get_table(self, table_name: str) -> DataFrame:
        return self._database[table_name]

    def set_database(self, database: dict[str, DataFrame]):
        self._database = database
        self._notify_observers()

    def set_table(self, table_name: str, table: DataFrame):
        self._database[table_name] = table
        self._notify_observers()

    def observe(self, callback):
        self._observers.append(callback)

    def _notify_observers(self):
        for callback in self._observers:
            callback(self._database)

    def create_row(self, table_name: str, columns: dict) -> bool:
        # Check for the table in the database
        if table_name not in self._database:
            return False

        # Try to add the row, catching errors for invalid column names
        try:
            self._database[table_name] = pd.concat([self._database[table_name], pd.Series(columns)], ignore_index=True)
        except ValueError as e:
            # TODO: Add more detailed error handling
            print(f"Error adding row to table {table_name}: {e}")
            return False

        self._notify_observers()

        return True

    def read_row(self, table_name: str, primary_key: str) -> Series:
        # Check for the table in the database
        if table_name not in self._database:
            return pd.Series()

        # Read the row from the database, or return an empty Series if not found
        return self._database[table_name].get(primary_key, pd.Series())

    def update_row(self, table_name: str, row: int, new_row_df: DataFrame) -> bool:
        # TODO: Fix updated method parameters
        # Check for the table in the database
        if table_name not in self._database:
            return False

        # Update the row in the database, or return False if not found
        if not new_row_df.index.difference(self._database[table_name].index).empty:
            return False
        else:
            self._database[table_name].update(new_row_df)
            self._notify_observers()
            return True

    def delete_row(self, table_name: str, primary_key: str) -> Series:
        # Check for the table in the database
        if table_name not in self._database:
            return pd.Series()

        # Delete the row from the database, or return an empty Series if not found
        removed_row = self._database[table_name].get(primary_key, pd.Series())

        if not removed_row.empty:
            self._database[table_name].drop(primary_key, inplace=True)

        self._notify_observers()

        return removed_row
