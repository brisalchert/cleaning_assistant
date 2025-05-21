from PyQt6.QtCore import pyqtSignal, QObject
from services import DatabaseService


class DatabaseLoaderWorker(QObject):
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, database_service: DatabaseService, connection_details: dict):
        super().__init__()
        self.database_service = database_service
        self.connection_details = connection_details

    def run(self):
        """Load the database using a separate thread."""
        try:
            self.progress.emit("Loading database...")
            success = self.database_service.load_from_database(self.connection_details)
            self.progress.emit("Database loaded successfully.")
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(f"Error loading database: {str(e)}")
            self.finished.emit(False)
