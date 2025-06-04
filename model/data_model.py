import pandas as pd
from pandas import DataFrame, Series


class DataModel:
    def __init__(self, database: dict[str, DataFrame] = None):
        self.database = database

    def set_database(self, database: dict[str, DataFrame]):
        self.database = database

    def read_table(self, table_name: str) -> DataFrame:
        return self.database[table_name]

    def create_row(self, table_name: str, columns: dict) -> bool:
        # Check for the table in the database
        if table_name not in self.database:
            return False

        # Try to add the row, catching errors for invalid column names
        try:
            self.database[table_name] = pd.concat([self.database[table_name], pd.Series(columns)], ignore_index=True)
        except ValueError as e:
            # TODO: Add more detailed error handling
            print(f"Error adding row to table {table_name}: {e}")
            return False

        return True

    def read_row(self, table_name: str, primary_key: str) -> Series:
        # Check for the table in the database
        if table_name not in self.database:
            return pd.Series()

        # Read the row from the database, or return an empty Series if not found
        return self.database[table_name].get(primary_key, pd.Series())

    def update_row(self, table_name: str, row: int, new_row_df: DataFrame) -> bool:
        # TODO: Fix updated method parameters
        # Check for the table in the database
        if table_name not in self.database:
            return False

        # Update the row in the database, or return False if not found
        if not new_row_df.index.difference(self.database[table_name].index).empty:
            return False
        else:
            self.database[table_name].update(new_row_df)
            return True

    def delete_row(self, table_name: str, primary_key: str) -> Series:
        # Check for the table in the database
        if table_name not in self.database:
            return pd.Series()

        # Delete the row from the database, or return an empty Series if not found
        removed_row = self.database[table_name].get(primary_key, pd.Series())

        if not removed_row.empty:
            self.database[table_name].drop(primary_key, inplace=True)

        return removed_row
