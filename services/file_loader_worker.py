from PyQt6.QtCore import QObject, pyqtSignal

from services import DatabaseService


class FileLoaderWorker(QObject):
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, database_service: DatabaseService, file_list: list[str]):
        super().__init__()
        self.database_service = database_service
        self.file_list = file_list

    def run(self):
        """Load the database from the file list using a separate thread."""
        try:
            self.progress.emit("Loading database into memory...")
            success = self.database_service.load_from_files(self.file_list)
            self.progress.emit("Database loaded successfully.")
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(f"Error loading database: {str(e)}")
            self.finished.emit(False)