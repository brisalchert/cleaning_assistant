import os
import re
import subprocess
from pathlib import Path

import pandas as pd
from fuzzywuzzy import process
from pandas import DataFrame

from model import DataModel
from services import AbstractService
from utils import Configuration


class DataCleaningService(AbstractService):
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
        if not pd.api.types.is_numeric_dtype(self._table[column]):
            raise ValueError(f"The \"{column}\" column is not numeric.")

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
        if not pd.api.types.is_numeric_dtype(self._table[column]):
            raise ValueError(f"The \"{column}\" column is not numeric.")

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
        mode_value = self._table[column].mode().iloc[0] if not self._table[column].mode().empty else None
        if mode_value is not None:
            self._table[column] = self._table[column].fillna(mode_value)
        after = self._table[column].isna().sum()
        self._model.set_table(self._table_name, self._table)

        return before - after

    def standardize(self, column: str):
        if not pd.api.types.is_numeric_dtype(self._table[column]):
            raise ValueError(f"The \"{column}\" column is not numeric.")

        mean = self._table[column].mean()
        std = self._table[column].std()

        self._table[column] = (self._table[column] - mean) / std
        self._model.set_table(self._table_name, self._table)

    def drop_missing(self, column: str) -> int:
        before = len(self._table)
        self._table = self._table.dropna(subset=[column])
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
        if not self._table[column].dtype == "category":
            raise ValueError(f"The \"{column}\" column is not categorical.")

        original = self._table[column].astype(str).copy()
        replaced = self._table[column].astype(str).replace(correction_map)

        self._table[column] = self._table[column].cat.rename_categories(correction_map)

        changed = (original != replaced).sum()
        self._model.set_table(self._table_name, self._table)

        return changed

    def autocorrect_categories(self, column: str, correct_categories: list[str]) -> int:
        if not self._table[column].dtype == "category":
            raise ValueError(f"The \"{column}\" column is not categorical.")

        original = self._table[column].astype(str).copy()
        replaced = self._table[column].astype(str).apply(lambda row: correct_spelling(row, correct_categories))

        new_categories = replaced.astype("category")

        self._table[column] = new_categories

        changed = (original != replaced).sum()
        self._model.set_table(self._table_name, self._table)

        return changed

    def trim_strings(self, column: str) -> int:
        original = self._table[column].copy()
        self._table[column] = self._table[column].str.strip()
        changed = self._table[column][original != self._table[column]].count()
        self._model.set_table(self._table_name, self._table)

        return changed

    def truncate_strings(self, column: str, max_length: int) -> int:
        if not pd.api.types.is_string_dtype(self._table[column]):
            raise ValueError(f"The \"{column}\" column is not a string data type.")

        original = self._table[column].copy()
        self._table[column] = self._table[column].str.slice(0, max_length)
        changed = self._table[column][original != self._table[column]].count()
        self._model.set_table(self._table_name, self._table)

        return changed

    def rename_column(self, column: str, new_name: str):
        self._table = self._table.rename(columns={column: new_name})
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
        if not pd.api.types.is_numeric_dtype(self._table[column]):
            raise ValueError(f"The \"{column}\" column is not numeric.")

        if minimum is None and maximum is None:
            q1 = self._table[column].quantile(0.25)
            q3 = self._table[column].quantile(0.75)
            iqr = q3 - q1

            minimum, maximum = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        elif minimum is not None and maximum is None:
            maximum = float("inf")
        elif minimum is None and maximum is not None:
            minimum = float("-inf")

        before = len(self._table)
        self._table = self._table[(self._table[column] >= minimum) & (self._table[column] <= maximum)]
        after = len(self._table)
        self._model.set_table(self._table_name, self._table)

        return before - after

    def drop_standard_outliers(self, column: str, upper: bool=False, lower: bool=False) -> int:
        q1 = self._table[column].quantile(0.25)
        q3 = self._table[column].quantile(0.75)

        if upper and lower:
            return self.drop_outliers(column, minimum=q1, maximum=q3)
        elif upper:
            return self.drop_outliers(column, maximum=q3)
        elif lower:
            return self.drop_outliers(column, minimum=q1)
        else:
            return 0

    def drop_date_outliers(self, column: str, minimum = None, maximum = None) -> int:
        if minimum is None and maximum is None:
            q1 = self._table[column].quantile(0.25)
            q3 = self._table[column].quantile(0.75)
            iqr = q3 - q1

            minimum, maximum = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        elif minimum is not None and maximum is None:
            maximum = pd.to_datetime("2100-01-01")
        elif minimum is None and maximum is not None:
            minimum = pd.to_datetime(0)

        before = len(self._table)
        self._table = self._table[(self._table[column] >= minimum) & (self._table[column] <= maximum)]
        after = len(self._table)
        self._model.set_table(self._table_name, self._table)

        return before - after

    def set_cleaning_script(self, script: str):
        # Validate cleaning script before loading
        if "# CLEANING ASSISTANT SCRIPT FILE" in script:
            self._cleaning_script = script

    def generate_cleaning_script(self, config: dict):
        """Generates a cleaning script for the current table and configuration."""
        lines = [
            "import pandas as pd",
            "from pathlib import Path",
            "from fuzzywuzzy import process",
            "def correct_spelling(row, categories: list):",
            "\tmatch = process.extractOne(row, categories)",
            "\tif match[1] >= 80:",
            "\t\treturn match[0]",
            "\telse:",
            "\t\treturn row",
            f"df = pd.read_csv('{self._table_name}.csv')"
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

        lines.append(f"desktop = Path.home() / 'Desktop'")
        lines.append(f"file_path = desktop / '{self._table_name}.csv'")

        lines.append(f"df.to_csv(file_path, index=False)")
        lines.append(f"print('Output saved to desktop.')")
        lines.append("# CLEANING ASSISTANT SCRIPT FILE")

        self._cleaning_script = "\n".join(lines)

    def save_cleaning_script(self, directory: str):
        if self._cleaning_script is None:
            raise ValueError("No cleaning script has been generated.")

        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)

        file_path = Path(f"{folder}/cleaning_script.py")
        file_path.write_text(self._cleaning_script)

    def apply_cleaning_script(self, script_path: str) -> bool:
        self._loaded_script_content = ""

        with open(script_path, "r") as file:
            self._loaded_script_content = file.read()

        lines = self._loaded_script_content.splitlines()
        if not lines[-1].startswith("# CLEANING ASSISTANT SCRIPT FILE"):
            return False

        # Temporarily place CSV file in current directory
        table_name = None
        for line in lines:
            match = re.search(r'read_csv\(\s*[\'"]([\w_]+)\.csv[\'"]\s*\)', line)
            if match:
                table_name = match.group(1)
                break

        if not table_name:
            return False

        csv_path = f"{table_name}.csv"

        self._model.get_table(table_name).to_csv(csv_path, index=False)

        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )

        # Remove temporary CSV
        if os.path.exists(csv_path):
            os.remove(csv_path)

        if result.returncode != 0:
            return False

        return True

def correct_spelling(row, categories: list):
    """Support function for correcting category spelling errors"""
    if pd.isna(row):
        return row

    match = process.extractOne(row, categories)
    if match[1] >= 80: # Similarity score threshold for replacement
        return match[0]
    else:
        return row
