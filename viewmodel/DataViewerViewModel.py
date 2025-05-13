from PyQt6.QtCore import pyqtSignal, QObject
from pandas import DataFrame
from navigation import Screen
from services import DataEditorService, QueryService
from viewmodel import ViewModel

class DataViewerViewModel(QObject, ViewModel):
    # --- Signals for view ---
    nav_destination_changed = pyqtSignal(Screen)
    data_changed = pyqtSignal(list[DataFrame])
    is_editing_changed = pyqtSignal(bool)
    query_result_changed = pyqtSignal(DataFrame)

    def __init__(self, data_editor_service: DataEditorService, query_service: QueryService):
        super().__init__()
        self.data_editor_service = data_editor_service
        self.query_service = query_service
        self._nav_destination = Screen.DATATABLE
        self._data = None
        self._is_editing = False
        self._query_result = None

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def load_table(self):
        # TODO: Implement load_table
        pass

    def toggle_editing(self):
        self._is_editing = not self._is_editing
        self.is_editing_changed.emit(self._is_editing)

    def update_row(self, primary_key: str, columns: dict):
        # TODO: Implement update_row
        pass

    def set_query_result(self, query_result: DataFrame):
        self._query_result = query_result
        self.query_result_changed.emit(query_result)
