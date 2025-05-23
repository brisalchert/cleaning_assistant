from PyQt6.QtCore import pyqtSignal, QThread
from navigation import Screen
from services import DatabaseService, DataEditorService, DatabaseLoaderWorker
from utils import generate_and_store_key
from utils.security import save_encrypted_db_credentials, load_key, delete_saved_db_credentials
from viewmodel import ViewModel


class MainViewModel(ViewModel):
    # --- Signals for view ---
    nav_destination_changed = pyqtSignal(Screen)
    data_changed = pyqtSignal(dict)
    database_loaded_changed = pyqtSignal(bool)
    database_loading_progress = pyqtSignal(str)
    database_loading_error = pyqtSignal(str)

    def __init__(self, database_service: DatabaseService, data_editor_service: DataEditorService):
        super().__init__()
        self.database_service = database_service
        self.data_editor_service = data_editor_service
        self._nav_destination = Screen.MAIN
        self._data = None
        self._database_loaded = None
        self.save_connection_parameters = False
        self.connection_details = None

        # Thread attributes
        self.worker_thread = None
        self.worker = None

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def load_database(self, db_name: str, user: str, host: str, password: str, port: int = 5432):
        """Load the database using a worker thread to avoid UI blocking"""
        self.connection_details = {
            "db_name": db_name,
            "user": user,
            "host": host,
            "password": password,
            "port": port
        }

        # Create worker and worker thread
        self.worker_thread = QThread()
        self.worker = DatabaseLoaderWorker(self.database_service, self.connection_details)
        self.worker.moveToThread(self.worker_thread)

        # Connect signals and slots
        self.worker.finished.connect(self.on_database_loading_finished)
        self.worker.error.connect(self.database_loading_error.emit)
        self.worker.progress.connect(self.database_loading_progress.emit)

        # Thread cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # Connect thread start to worker task
        self.worker_thread.started.connect(self.worker.run)

        # Start worker thread
        self._database_loaded = False
        self.worker_thread.start()

    def set_save_credentials(self, save_credentials: bool):
        self.save_connection_parameters = save_credentials

    def on_database_loading_finished(self, success: bool):
        """Handle database loading completion"""
        if success:
            # Save or delete connection parameters
            if self.save_connection_parameters:
                save_encrypted_db_credentials(**self.connection_details, key=load_key())
            else:
                delete_saved_db_credentials()

            self._data = self.database_service.get_tables()
            self._database_loaded = True
            self.data_changed.emit(self._data)
            self.database_loaded_changed.emit(self._database_loaded)
        else:
            self._database_loaded = False
            self.database_loaded_changed.emit(False)
            delete_saved_db_credentials()

        # Remove connection details from view model
        self.connection_details = None

    def load_file(self, file_path: str):
        self.database_service.load_from_file(file_path)

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

    def export_data(self):
        self.data_editor_service.export_data()
