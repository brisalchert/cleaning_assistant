from PyQt6.QtCore import pyqtSignal
from pandas import DataFrame
from pandasql import PandaSQLException

from navigation import Screen
from services import DataEditorService, QueryService
from viewmodel import ViewModel


class DataViewerViewModel(ViewModel):
    # --- Signals for view ---
    nav_destination_changed: pyqtSignal = pyqtSignal(Screen)
    data_changed: pyqtSignal = pyqtSignal(dict)
    is_editing_changed: pyqtSignal = pyqtSignal(bool)
    query_result_changed: pyqtSignal = pyqtSignal(DataFrame)
    query_error_changed: pyqtSignal = pyqtSignal(str)
    undo_available_changed: pyqtSignal = pyqtSignal(bool)
    redo_available_changed: pyqtSignal = pyqtSignal(bool)

    def __init__(self, data_editor_service: DataEditorService, query_service: QueryService):
        super().__init__()
        self.data_editor_service = data_editor_service
        self.query_service = query_service
        self._nav_destination = Screen.DATA_TABLE
        self._table_name = None
        self._data = None
        self._is_editing = False
        self._query_result = None

        # Connect to model updates
        self.data_editor_service.model.data_changed.connect(self.on_database_update)

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def on_database_update(self, database: dict[str, DataFrame]):
        if self._table_name:
            self._data = database[self._table_name]
            self.data_changed.emit({"table_name": self._table_name, "data": self._data.copy(deep=True)})

    def set_table(self, table_name: str):
        # Set and retrieve table in the service
        self.data_editor_service.set_table(table_name)
        self._table_name = table_name
        self._data = self.data_editor_service.get_current_table()
        self.data_changed.emit({"table_name": self._table_name, "data": self._data.copy(deep=True)})

    def toggle_editing(self):
        self._is_editing = not self._is_editing
        self.is_editing_changed.emit(self._is_editing)

    def emit_update_signals(self):
        self.undo_available_changed.emit(self.data_editor_service.get_undo_available())
        self.redo_available_changed.emit(self.data_editor_service.get_redo_available())

    def update_row(self, row: int, new_row_df: DataFrame):
        self.data_editor_service.update_row(self._table_name, row, new_row_df)
        self._data = self.data_editor_service.get_current_table()
        self.emit_update_signals()

    def set_query_result(self, query_result: DataFrame):
        self._query_result = query_result
        self.query_result_changed.emit(query_result)

    def execute_query(self, query: str):
        self.query_service.set_query(query)
        result = None

        try:
            result = self.query_service.execute_query()
        except PandaSQLException as e:
            self.query_error_changed.emit(str(e))

        if result is not None:
            self.set_query_result(result)

    def undo_change(self):
        self.data_editor_service.undo_change()
        self._data = self.data_editor_service.get_current_table()
        self.emit_update_signals()

    def redo_change(self):
        self.data_editor_service.redo_change()
        self._data = self.data_editor_service.get_current_table()
        self.emit_update_signals()
