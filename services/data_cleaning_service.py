import io
from pandas import Series, DataFrame
from model import DataModel
from services import AbstractService, ModelEditor


class DataCleaningService(AbstractService, ModelEditor):
    @property
    def model(self) -> DataModel:
        return self._model

    @property
    def cleaningScript(self) -> io.TextIOWrapper:
        return self._cleaningScript

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def table(self) -> DataFrame:
        return self._table

    def __init__(self, model: DataModel):
        self._model = model
        self._cleaningScript = None
        self._table_name = None
        self._table = None

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

    def set_and_retrieve_table(self, table_name: str):
        self._table = {table_name: self._model.database[table_name]}
        return self._table

    def calculate_missingness(self, column: str) -> Series:
        # TODO: Implement calculate_missingness
        pass

    def impute_missing(self, column: str, statistic: float):
        # TODO: Implement impute_missing
        pass

    def drop_missing(self, column: str):
        # TODO: Implement drop_missing
        pass

    def get_categories(self, column: str):
        # TODO: Implement get_categories
        pass

    def clean_categories(self, column: str, correction_map: dict):
        # TODO: Implement clean_categories
        pass

    def trim_strings(self, column: str):
        # TODO: Implement trim_strings
        pass

    def rename_column(self, column: str, new_name: str):
        # TODO: Implement rename_column
        pass

    def get_data_type(self, column: str):
        # TODO: Implement get_data_type
        pass

    def clean_duplicates(self, column: str):
        # TODO: Implement clean_duplicates
        pass

    def get_outliers(self, column: str) -> DataFrame:
        # TODO: Implement get_outliers
        pass

    def drop_outliers(self, column: str, minimum: float = None, maximum: float = None):
        # TODO: Implement drop_outliers
        pass

    def set_cleaning_script(self, script: io.TextIOWrapper):
        # TODO: Implement set_cleaning_script
        pass

    def save_cleaning_script(self):
        # TODO: Implement save_cleaning_script
        pass

    def apply_cleaning_script(self):
        # TODO: Implement apply_cleaning_script
        pass
