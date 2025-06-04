from PyQt6.QtCore import pyqtSignal, QThread

from navigation import Screen
from services import DataEditorService, DatabaseExportWorker, DatabaseServiceWrapper
from workers import DatabaseLoaderWorker, FileLoaderWorker
from utils.security import save_encrypted_db_credentials, load_key, delete_saved_db_credentials
from viewmodel import ViewModel


class MainViewModel(ViewModel):
    # --- Signals for view ---
    nav_destination_changed: pyqtSignal = pyqtSignal(Screen)
    data_changed: pyqtSignal = pyqtSignal(dict)
    database_loaded_changed: pyqtSignal = pyqtSignal(bool)
    database_loading_progress: pyqtSignal = pyqtSignal(str)
    database_loading_error: pyqtSignal = pyqtSignal(str)
    exporting_changed: pyqtSignal = pyqtSignal(bool)
    exporting_completion: pyqtSignal = pyqtSignal(str)
    exporting_error: pyqtSignal = pyqtSignal(str)

    def __init__(self, database_service_wrapper: DatabaseServiceWrapper, data_editor_service: DataEditorService):
        super().__init__()
        self.database_service_wrapper = database_service_wrapper
        self.database_service = database_service_wrapper.database_service
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

        self.worker = DatabaseLoaderWorker(self.database_service_wrapper, self.connection_details)
        self._database_loaded = False
        self.start_worker(self.on_database_loading_finished, self.database_loading_error, self.database_loading_progress)

    def load_files(self, file_list: list[str], csv_config: dict):
        self.worker = FileLoaderWorker(self.database_service_wrapper, file_list, csv_config)
        self._database_loaded = False
        self.start_worker(self.on_file_loading_finished, self.database_loading_error, self.database_loading_progress)

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

    def on_file_loading_finished(self, success: bool):
        if success:
            self._data = self.database_service.get_tables()
            self._database_loaded = True
            self.data_changed.emit(self._data)
            self.database_loaded_changed.emit(self._database_loaded)
        else:
            self._database_loaded = False
            self.database_loaded_changed.emit(False)

    def start_worker(self, on_finished, error_signal, progress_signal=None):
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # Connect signals and slots
        self.worker.finished.connect(on_finished)
        self.worker.error.connect(error_signal.emit)
        if progress_signal is not None:
            self.worker.progress.connect(progress_signal.emit)

        # Thread cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.worker_thread.deleteLater)

        # Connect thread start to worker task
        self.worker_thread.started.connect(self.worker.run)

        # Start worker thread
        self.worker_thread.start()

    def export_data(self, directory: str):
        self.worker = DatabaseExportWorker(self.data_editor_service, directory)
        self.exporting_changed.emit(True)
        self.start_worker(self.on_exporting_finished, self.exporting_error)

    def on_exporting_finished(self, success: bool):
        if success:
            self.exporting_completion.emit("Database exported successfully.")

        self.exporting_changed.emit(False)
