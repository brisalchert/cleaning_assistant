from PyQt6.QtCore import QObject, pyqtSignal

from services import DatabaseServiceWrapper


class FileLoaderWorker(QObject):
    finished: pyqtSignal = pyqtSignal(bool)
    error: pyqtSignal = pyqtSignal(str)
    progress: pyqtSignal = pyqtSignal(str)

    def __init__(self, database_service_wrapper: DatabaseServiceWrapper, file_list: list[str], csv_config: dict):
        super().__init__()
        self.database_service_wrapper = database_service_wrapper
        self.file_list = file_list
        self.csv_config = csv_config

    def run(self):
        """Load the database from the file list using a separate thread."""
        try:
            self.progress.emit("Loading database into memory...")
            success = self.database_service_wrapper.load_from_files(self.file_list, self.csv_config)
            self.progress.emit("Database loaded successfully.")
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(f"Error loading database: {str(e)}")
            self.finished.emit(False)
