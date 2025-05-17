from pandas import DataFrame, Series


class DataModel:
    def __init__(self, database: dict[str, DataFrame] = None):
        self.database = database

    def set_database(self, database: dict[str, DataFrame]):
        self.database = database

    def read_table(self, table_name: str) -> DataFrame:
        return self.database[table_name]

    def create_row(self, table_name: str, columns: dict) -> bool:
        # TODO: Implement create_row
        pass

    def read_row(self, table_name: str, primary_key: str) -> Series:
        # TODO: Implement read_row
        pass

    def update_row(self, table_name: str, primary_key: str, columns: dict) -> bool:
        # TODO: Implement update_row
        pass

    def delete_row(self, table_name: str, primary_key: str) -> Series:
        # TODO: Implement delete_row
        pass
