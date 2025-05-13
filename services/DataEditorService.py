import pandas as pd
from pandas import Series, DataFrame
from model import DataModel
from services import AbstractService
from services import ModelEditor


class DataEditorService(AbstractService, ModelEditor):
    @property
    def model(self) -> DataModel:
        return self._model

    def __init__(self, model: DataModel):
        self._model = model
        self.current_table: DataFrame = pd.DataFrame()
        self.undo_stack: list[DataFrame] = []
        self.redo_stack: list[DataFrame] = []

    # --- ModelEditor overrides ---

    def create_row(self, table_name: str, columns: dict) -> bool:
        self.undo_stack.append(self.current_table)

        return self._model.create_row(table_name, columns)

    def read_row(self, table_name: str, primary_key: str) -> Series:
        return self._model.read_row(table_name, primary_key)

    def update_row(self, table_name: str, primary_key: str, columns: dict) -> bool:
        self.undo_stack.append(self.current_table)

        return self._model.update_row(table_name, primary_key, columns)

    def delete_row(self, table_name: str, primary_key: str) -> Series:
        self.undo_stack.append(self.current_table)

        return self._model.delete_row(table_name, primary_key)

    # --- Subclass methods ---

    def set_table(self, table_name: str):
        self.current_table = self._model.read_table(table_name)

    def get_current_table(self) -> DataFrame:
        return self.current_table

    def undo_change(self):
        if len(self.undo_stack) > 0:
            self.redo_stack.append(self.current_table)
            self.current_table = self.undo_stack.pop()

    def redo_change(self):
        if len(self.redo_stack) > 0:
            self.undo_stack.append(self.current_table)
            self.current_table = self.redo_stack.pop()

    def export_data(self):
        # TODO: Define export_data
        pass
