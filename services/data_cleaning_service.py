import subprocess
from pathlib import Path

import pandas as pd
from fuzzywuzzy import process
from pandas import Series, DataFrame

from model import DataModel
from services import AbstractService, ModelEditor
from utils import Configuration


class DataCleaningService(AbstractService, ModelEditor):
    @property
    def model(self) -> DataModel:
        return self._model

    @property
    def cleaning_script(self) -> str:
        return self._cleaning_script

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def table(self) -> DataFrame:
        return self._table

    def __init__(self, model: DataModel):
        self._model = model
        self._cleaning_script = None
        self._loaded_script_content = None
        self._table_name = None
        self._table: DataFrame = pd.DataFrame()

    # --- ModelEditor overrides ---

    def create_row(self, table_name: str, columns: dict) -> bool:
        return self._model.create_row(table_name, columns)

    def read_row(self, table_name: str, primary_key: str) -> Series:
        return self._model.read_row(table_name, primary_key)

    def update_row(self, table_name: str, primary_key: str, columns: dict) -> bool:
        # TODO: FIX THIS
        return self._model.update_row(table_name, primary_key, columns)

    def delete_row(self, table_name: str, primary_key: str) -> Series:
        return self._model.delete_row(table_name, primary_key)

    # --- Subclass methods ---

    def set_and_retrieve_table(self, table_name: str) -> dict:
        self._table_name = table_name
        self._table = self._model.get_table(table_name)
        return {table_name: self._table}

    def calculate_missingness(self, column: str):
        missing = self._table[column].isna()

        return missing.sum()

    def set_data_type(self, column: str, data_type: str) -> int:
        if self._table[column].dtype != data_type:
            if data_type == "int64":
                self._table[column] = pd.to_numeric(self._table[column], errors="coerce")
                try:
                    self._table[column] = self._table[column].astype("int64")
                except ValueError:
                    # Use nullable integer data type
                    self._table[column] = self._table[column].astype("Int64")
            elif data_type == "float64":
                self._table[column] = pd.to_numeric(self._table[column], errors="coerce")
                self._table[column] = self._table[column].astype(data_type)
            elif data_type == "datetime64[ns]":
                self._table[column] = pd.to_datetime(self._table[column], errors="coerce")
            else:
                self._table[column] = self._table[column].astype(data_type)
            self._model.set_table(self._table_name, self._table)

            return 1

        return 0

    def impute_missing_mean(self, column: str) -> int:
        before = self._table[column].isna().sum()
        self._table[column] = self._table[column].fillna(self._table[column].mean())
        after = self._table[column].isna().sum()
        self._model.set_table(self._table_name, self._table)

        return before - after

    def impute_missing_mean_all(self) -> int:
        before = self._table.isna().sum().sum()
        self._table = self._table.fillna(self._table.mean(numeric_only=True))
        after = self._table.isna().sum().sum()
        self._model.set_table(self._table_name, self._table)

        return before - after

    def impute_missing_median(self, column: str) -> int:
        before = self._table[column].isna().sum()
        self._table[column] = self._table[column].fillna(self._table[column].median())
        after = self._table[column].isna().sum()
        self._model.set_table(self._table_name, self._table)

        return before - after

    def impute_missing_median_all(self) -> int:
        before = self._table.isna().sum().sum()
        self._table = self._table.fillna(self._table.median(numeric_only=True))
        after = self._table.isna().sum().sum()
        self._model.set_table(self._table_name, self._table)

        return before - after

    def impute_missing_mode(self, column: str) -> int:
        before = self._table[column].isna().sum()
        self._table = self._table[column].fillna(self._table.mode())
        after = self._table[column].isna().sum()
        self._model.set_table(self._table_name, self._table)

        return before - after

    def standardize(self, column: str):
        mean = self._table[column].mean()
        std = self._table[column].std()

        self._table[column] = (self._table[column] - mean) / std
        self._model.set_table(self._table_name, self._table)

    def drop_missing(self, column: str) -> int:
        before = len(self._table)
        self._table[column] = self._table[column].dropna()
        after = len(self._table)
        self._model.set_table(self._table_name, self._table)

        return before - after

    def drop_missing_all(self) -> int:
        before = len(self._table)
        self._table = self._table.dropna()
        after = len(self._table)
        self._model.set_table(self._table_name, self._table)

        return before - after

    def get_categories(self, column: str):
        if self._table[column].dtype == "category":
            return self._table[column].cat.categories
        else:
            return self._table[column].unique()

    def clean_categories(self, column: str, correction_map: dict) -> int:
        original = self._table[column].copy()
        self._table[column] = self._table[column].replace(correction_map)
        changed = self._table[column][original != self._table[column]].count()
        self._table[column] = self._table[column].astype("category")
        self._model.set_table(self._table_name, self._table)

        return changed

    def autocorrect_categories(self, column: str, correct_categories: list) -> int:
        original = self._table[column].copy()
        self._table[column] = self._table[column].apply(lambda row: correct_spelling(row, correct_categories))
        changed = self._table[column][original != self._table[column]].count()
        self._table[column] = self._table[column].astype("category")
        self._model.set_table(self._table_name, self._table)

        return changed

    def trim_strings(self, column: str) -> int:
        original = self._table[column].copy()
        self._table[column] = self._table[column].str.strip()
        changed = self._table[column][original != self._table[column]].count()
        self._model.set_table(self._table_name, self._table)

        return changed

    def truncate_strings(self, column: str, max_length: int) -> int:
        original = self._table[column].copy()
        self._table[column] = self._table[column].str.slice(0, max_length)
        changed = self._table[column][original != self._table[column]].count()
        self._model.set_table(self._table_name, self._table)

        return changed

    def rename_column(self, column: str, new_name: str):
        self._table[column] = self._table[column].rename(new_name)
        self._model.set_table(self._table_name, self._table)

    def get_data_type(self, column: str):
        return self._table[column].dtype

    def get_table_length(self):
        return self._table.shape[0]

    def drop_duplicates(self) -> int:
        before = len(self._table)
        self._table = self._table.drop_duplicates()
        after = len(self._table)
        self._model.set_table(self._table_name, self._table)

        return before - after

    def get_outliers(self, column: str) -> DataFrame:
        q1 = self._table[column].quantile(0.25)
        q3 = self._table[column].quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        df_outliers = self._table[(self._table[column] < lower_bound) | (self._table[column] > upper_bound)]
        return df_outliers

    def drop_outliers(self, column: str, minimum: float = None, maximum: float = None) -> int:
        if minimum is None or maximum is None:
            q1 = self._table[column].quantile(0.25)
            q3 = self._table[column].quantile(0.75)
            iqr = q3 - q1

            minimum, maximum = q1 - 1.5 * iqr, q3 + 1.5 * iqr

        before = len(self._table)
        self._table = self._table[(self._table[column] >= minimum) & (self._table[column] <= maximum)]
        after = len(self._table)
        self._model.set_table(self._table_name, self._table)

        return before - after

    def drop_date_outliers(self, column: str, minimum = None, maximum = None) -> int:
        if minimum is not None and maximum is not None:
            before = len(self._table)
            self._table[column] = self._table[(self._table[column] >= minimum) & (self._table[column] <= maximum)]
            after = len(self._table)
            self._model.set_table(self._table_name, self._table)

            return before - after
        return 0

    def set_cleaning_script(self, script: str):
        # Validate cleaning script before loading
        if script.__contains__("# CLEANING ASSISTANT SCRIPT FILE"):
            self._cleaning_script = script

    def generate_cleaning_script(self, config: dict):
        """Generates a cleaning script for the current table and configuration."""
        lines = [
            "import pandas as pd",
            "from fuzzywuzzy import process",
            "def correct_spelling(row, categories: list):",
            "\tmatch = process.extractOne(row, categories)",
            "\tif match[1] >= 80:",
            "\t\treturn match[0]",
            "\telse:",
            "\t\treturn row",
            f"df = pd.read_csv({self._table_name}.csv)"
        ]

        # Column-specific cleaning
        for column, options in config[Configuration.COLUMNS].items():
            for key, value in options.items():
                if key == Configuration.DATA_TYPE:
                    if self._table[column].dtype != value:
                        if value == "int64":
                            lines.append(f"df[{column}] = pd.to_numeric(df[{column}], errors='coerce')")
                            lines.append(f"try:")
                            lines.append(f"\tdf[{column}] = df[{column}].astype({value})")
                            lines.append(f"except ValueError:")
                            lines.append(f"\tdf[{column}] = df[{column}].astype('Int64')")
                        elif value == "float64":
                            lines.append(f"df[{column}] = pd.to_numeric(df[{column}], errors='coerce')")
                            lines.append(f"df[{column}] = df[{column}].astype('float64')")
                        elif value == "datetime64[ns]":
                            lines.append(f"df[{column}] = pd.to_datetime(df[{column}], errors='coerce')")
                        else:
                            lines.append(f"df[{column}] = df[{column}].astype({value})")
                elif key == Configuration.INT_MIN:
                    lines.append(f"df[{column}] = df[df[{column}] >= {value}]")
                elif key == Configuration.INT_MAX:
                    lines.append(f"df[{column}] = df[df[{column}] <= {value}]")
                elif key == Configuration.FLOAT_MIN:
                    lines.append(f"df[{column}] = df[df[{column}] >= {value}]")
                elif key == Configuration.FLOAT_MAX:
                    lines.append(f"df[{column}] = df[df[{column}] <= {value}]")
                elif key == Configuration.STRING_MAX:
                    lines.append(f"df[{column}] = df[{column}].str.slice(0, {value})")
                elif key == Configuration.DATE_MIN:
                    lines.append(f"df[{column}] = df[df[{column}] >= {value}]")
                elif key == Configuration.DATE_MAX:
                    lines.append(f"df[{column}] = df[df[{column}] <= {value}]")
                elif key == Configuration.CATEGORIES:
                    lines.append(f"df[{column}] = df[{column}].apply(lambda row: correct_spelling(row, {value}))")
                    lines.append(f"df[{column}] = df[{column}].astype('category')")

        # General cleaning options
        if config[Configuration.DELETE_DUPLICATES]:
            lines.append(f"df = df.drop_duplicates()")

        if config[Configuration.DROP_MISSING]:
            lines.append(f"df = df.dropna()")
        elif config[Configuration.IMPUTE_MISSING_MEAN]:
            for column in self._table.columns:
                lines.append(f"df[{column}] = df[{column}].fillna(df[{column}].mean())")
        elif config[Configuration.IMPUTE_MISSING_MEDIAN]:
            for column in self._table.columns:
                lines.append(f"df[{column}] = df[{column}].fillna(df[{column}].median())")

        lines.append(f"df.to_csv('{self._table_name}.csv', index=False)")
        lines.append(f"print('Output saved to {self._table_name}.csv')")
        lines.append("# CLEANING ASSISTANT SCRIPT FILE")

        self._cleaning_script = "\n".join(lines)

    def save_cleaning_script(self, directory: str):
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)

        file_path = Path(f"{folder}/cleaning_script.py")
        file_path.write_text(self._cleaning_script)

    def apply_cleaning_script(self, script_path: str):
        self._loaded_script_content = ""

        with open(script_path, "r") as file:
            self._loaded_script_content = file.read()

        lines = self._loaded_script_content.splitlines()
        if not lines[-1].startswith("# CLEANING ASSISTANT SCRIPT FILE"):
            return

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )
        # TODO: Connect output with messaging in view (use a new worker)
        print("Result: ", result.stdout)

def correct_spelling(row, categories: list):
    """Support function for correcting category spelling errors"""
    match = process.extractOne(row, categories)
    if match[1] >= 80: # Similarity score threshold for replacement
        return match[0]
    else:
        return row
