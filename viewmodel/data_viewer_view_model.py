from PyQt6.QtCore import pyqtSignal
from pandas import DataFrame
from pandasql import PandaSQLException
from navigation import Screen
from services import DataEditorService, QueryService
from viewmodel import ViewModel


class DataViewerViewModel(ViewModel):
    # --- Signals for view ---
    nav_destination_changed = pyqtSignal(Screen)
    data_changed = pyqtSignal(dict)
    is_editing_changed = pyqtSignal(bool)
    query_result_changed = pyqtSignal(DataFrame)
    query_error_changed = pyqtSignal(str)

    def __init__(self, data_editor_service: DataEditorService, query_service: QueryService):
        super().__init__()
        self.data_editor_service = data_editor_service
        self.query_service = query_service
        self._nav_destination = Screen.DATA_TABLE
        self._table_name = None
        self._data = None
        self._is_editing = False
        self._query_result = None

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def set_table(self, table_name: str):
        # Set and retrieve table in the service
        self.data_editor_service.set_table(table_name)
        self._table_name = table_name
        self._data = self.data_editor_service.get_current_table()
        self.data_changed.emit({"table_name": self._table_name, "data": self._data})

    def toggle_editing(self):
        self._is_editing = not self._is_editing
        self.is_editing_changed.emit(self._is_editing)

    def update_row(self, primary_key: str, columns: dict):
        self.data_editor_service.update_row(self._table_name, primary_key, columns)
        self._data = self.data_editor_service.get_current_table()
        self.data_changed.emit({self._table_name: self._data})

    def set_query_result(self, query_result: DataFrame):
        self._query_result = query_result
        self.query_result_changed.emit(query_result)

    def execute_query(self, query: str):
        self.query_service.set_query(query)
        result = None

        try:
            result = self.query_service.execute_query()
        except PandaSQLException as e:
            print(f"PandaSQL Error: {str(e)}")
            self.query_error_changed.emit(str(e))

        if result is not None:
            self.set_query_result(result)
