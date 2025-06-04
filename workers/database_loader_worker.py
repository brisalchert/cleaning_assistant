from PyQt6.QtCore import pyqtSignal, QObject

from services import DatabaseServiceWrapper


class DatabaseLoaderWorker(QObject):
    finished: pyqtSignal = pyqtSignal(bool)
    error: pyqtSignal = pyqtSignal(str)
    progress: pyqtSignal = pyqtSignal(str)

    def __init__(self, database_service_wrapper: DatabaseServiceWrapper, connection_details: dict):
        super().__init__()
        self.database_service_wrapper = database_service_wrapper
        self.connection_details = connection_details

    def run(self):
        """Load the database using a separate thread."""
        try:
            self.progress.emit("Loading database into memory...")
            success = self.database_service_wrapper.load_from_database(self.connection_details)
            self.progress.emit("Database loaded successfully.")
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(f"Error loading database: {str(e)}")
            self.finished.emit(False)
