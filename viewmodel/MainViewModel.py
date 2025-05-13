from PyQt6.QtCore import pyqtSignal
from pandas import DataFrame
from navigation import Screen
from services import DatabaseService, DataEditorService
from viewmodel import ViewModel


class MainViewModel(ViewModel):
    @property
    def nav_destination(self) -> Screen:
        return self._nav_destination

    @property
    def data_changed(self) -> pyqtSignal(list[DataFrame]):
        return self._data_changed

    @property
    def database_loaded(self) -> pyqtSignal(bool):
        return self._database_loaded

    def __init__(self, database_service: DatabaseService, data_editor_service: DataEditorService):
        self.database_service = database_service
        self.data_editor_service = data_editor_service
        self._nav_destination = Screen.MAIN
        self._data_changed = None
        self._database_loaded = False

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination

    def load_database(self, database: str, user: str, host: str, password: str, port: int = 5432):
        self.database_service.set_connection(database, user, host, password, port)

    def load_file(self, file_path: str):
        self.database_service.set_file(file_path)

    def reset_data(self):
        self.database_service.reset_data()

    def undo_change(self):
        self.data_editor_service.undo_change()

    def redo_change(self):
        self.data_editor_service.redo_change()

    def enter_table_view(self):
        # TODO: Implement enter_table_view
        pass

    def export_data(self):
        self.data_editor_service.export_data()

    def navigate_to(self, destination: Screen):
        self.set_nav_destination(destination)
