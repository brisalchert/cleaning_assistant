from pathlib import Path

import pandas as pd
from pandas import Series, DataFrame

from model import DataModel
from services import AbstractService


def get_dataframe_diff(table_name: str, old_row_df: DataFrame, new_row_df: DataFrame) -> list[dict]:
    # Ensure the input is single-row dataframes
    assert len(old_row_df) == 1, "old_df must represent a single row"
    assert len(new_row_df) == 1, "new_df must represent a single row"

    # Check for compatible columns and index
    assert old_row_df.columns.equals(new_row_df.columns), "Dataframes have incompatible columns"
    assert old_row_df.index.equals(new_row_df.index), "Dataframes have incompatible indices"

    # Get the true row index
    row = old_row_df.index[0]

    diffs = []
    for col in old_row_df.columns:
        old_val = old_row_df.at[row, col]
        new_val = new_row_df.at[row, col]
        if old_val != new_val:
            diffs.append({
                "table": table_name,
                "row": row,
                "column": col,
                "old_value": old_val,
                "new_value": new_val
            })

    return diffs


class DataEditorService(AbstractService):
    @property
    def model(self) -> DataModel:
        return self._model

    def __init__(self, model: DataModel):
        self._model = model
        self.current_table: DataFrame = pd.DataFrame()
        self.undo_stack: list[list[dict]] = []
        self.redo_stack: list[list[dict]] = []

    def update_row(self, table_name: str, row: int, new_row_df: DataFrame) -> bool:
        # TODO: Check data types when making edits
        old_row_df = self._model.get_table(table_name).iloc[[row]].copy(deep=True)
        result = self._model.update_row(table_name, row, new_row_df)

        # Update undo stack
        if result:
            self.undo_stack.append(get_dataframe_diff(table_name, old_row_df, new_row_df))

        return result

    def set_table(self, table_name: str):
        self.current_table = self._model.get_table(table_name)

    def get_current_table(self) -> DataFrame:
        return self.current_table

    def undo_change(self):
        if len(self.undo_stack) > 0:
            # Update redo stack
            diffs = self.undo_stack.pop()
            self.redo_stack.append(diffs)

            updated_tables = {}

            # Apply undo
            for diff in diffs:
                table_name = diff["table"]

                if table_name not in updated_tables:
                    updated_tables[table_name] = self._model.get_table(table_name).copy(deep=True)

                updated_tables[table_name].at[diff["row"], diff["column"]] = diff["old_value"]

            # Trigger updates in the model
            for table_name, updated_df in updated_tables.items():
                self._model.set_table(table_name, updated_df)

    def redo_change(self):
        if len(self.redo_stack) > 0:
            # Update undo stack
            diffs = self.redo_stack.pop()
            self.undo_stack.append(diffs)

            updated_tables = {}

            # Apply redo
            for diff in diffs:
                table_name = diff["table"]

                if table_name not in updated_tables:
                    updated_tables[table_name] = self._model.get_table(table_name).copy(deep=True)

                updated_tables[table_name].at[diff["row"], diff["column"]] = diff["new_value"]

            # Trigger updates in the model
            for table_name, updated_df in updated_tables.items():
                self._model.set_table(table_name, updated_df)

    def export_data(self, directory: str) -> bool:
        # Create directory for export files
        path = Path(f"{directory}/cleaning_assistant_export")
        path.mkdir(parents=True, exist_ok=True)

        for name, df in self._model.get_database().items():
            file_name = f"{name}.csv"
            file_path = Path(f"{path}/{file_name}")

            df.to_csv(file_path, index=False)

        return True

    def get_undo_available(self) -> bool:
        if self.undo_stack:
            return True
        else:
            return False

    def get_redo_available(self) -> bool:
        if self.redo_stack:
            return True
        else:
            return False
