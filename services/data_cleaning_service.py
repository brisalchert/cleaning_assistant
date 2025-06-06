import io

import pandas as pd
from fuzzywuzzy import process
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
        self._table: DataFrame = pd.DataFrame()

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

    def set_and_retrieve_table(self, table_name: str) -> dict:
        self._table_name = table_name
        self._table = self._model._database[table_name]
        return {table_name: self._table}

    def calculate_missingness(self, column: str):
        missing = self._table[column].isna()

        return missing.sum()


    def impute_missing_mean(self, column: str):
        self._table = self._table[column].fillna(self._table[column].mean())
        self._model.set_table(self._table_name, self._table)

    def impute_missing_median(self, column: str):
        self._table = self._table[column].fillna(self._table[column].median())
        self._model.set_table(self._table_name, self._table)

    def drop_missing(self, column: str):
        self._table = self._table[column].dropna()
        self._model.set_table(self._table_name, self._table)

    def get_categories(self, column: str):
        if self._table[column].dtype == "category":
            return self._table[column].cat.categories
        else:
            return self._table[column].unique()

    def clean_categories(self, column: str, correction_map: dict):
        self._table[column] = self._table[column].replace(correction_map)
        self._table[column] = self._table[column].astype("category")
        self._model.set_table(self._table_name, self._table)

    def autocorrect_categories(self, column: str, correct_categories: list):
        self._table[column] = self._table[column].apply(lambda row: correct_spelling(row, correct_categories))
        self._table[column] = self._table[column].astype("category")
        self._model.set_table(self._table_name, self._table)

    def trim_strings(self, column: str):
        self._table[column] = self._table[column].str.strip()
        self._model.set_table(self._table_name, self._table)

    def rename_column(self, column: str, new_name: str):
        self._table[column] = self._table[column].rename(new_name)
        self._model.set_table(self._table_name, self._table)

    def get_data_type(self, column: str):
        return self._table[column].dtype

    def drop_duplicates(self, column: str):
        self._table[column] = self._table[column].drop_duplicates()
        self._model.set_table(self._table_name, self._table)

    def get_outliers(self, column: str) -> DataFrame:
        q_low = self._table[column].quantile(0.01)
        q_high = self._table[column].quantile(0.99)

        df_outliers = self._table[(self._table[column] < q_low) | (self._table[column] > q_high)]
        return df_outliers

    def drop_outliers(self, column: str, minimum: float = None, maximum: float = None):
        if minimum is None or maximum is None:
            minimum, maximum = self._table[column].quantile(0.01), self._table[column].quantile(0.99)

        self._table = self._table[(self._table[column] > minimum) & (self._table[column] < maximum)]
        self._model.set_table(self._table_name, self._table)

    def set_cleaning_script(self, script: io.TextIOWrapper):
        # TODO: Implement set_cleaning_script
        pass

    def save_cleaning_script(self):
        # TODO: Implement save_cleaning_script
        pass

    def apply_cleaning_script(self):
        # TODO: Implement apply_cleaning_script
        pass

def correct_spelling(row, categories: list):
    """Support function for correcting category spelling errors"""
    match = process.extractOne(row, categories)
    if match[1] >= 80: # Similarity score threshold for replacement
        return match[0]
    else:
        return row
