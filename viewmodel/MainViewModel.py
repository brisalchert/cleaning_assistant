from PyQt6.QtCore import pyqtSignal, QObject
from pandas import DataFrame
from navigation import Screen
from services import DatabaseService, DataEditorService
from viewmodel import ViewModel


class MainViewModel(QObject, ViewModel):
    # --- Signals for view ---
    nav_destination_changed = pyqtSignal(Screen)
    data_changed = pyqtSignal(dict[str, DataFrame])
    database_loaded_changed = pyqtSignal(bool)

    def __init__(self, database_service: DatabaseService, data_editor_service: DataEditorService):
        super().__init__()
        self.database_service = database_service
        self.data_editor_service = data_editor_service
        self._nav_destination = Screen.MAIN
        self._data = None
        self._database_loaded = None

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def load_database(self, database: str, user: str, host: str, password: str, port: int = 5432):
        self.database_service.set_connection(database, user, host, password, port)
        self.database_service.load_from_database()
        self._data = self.database_service.get_tables()
        self._database_loaded = True
        self.data_changed.emit(self._data)
        self.database_loaded_changed.emit(self._database_loaded)

    def load_file(self, file_path: str):
        self.database_service.set_file(file_path)
        self.database_service.load_from_file()
        self._data = self.database_service.get_tables()
        self._database_loaded = True
        self.data_changed.emit(self._data)
        self.database_loaded_changed.emit(self._database_loaded)

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
