from PyQt6.QtCore import pyqtSignal, QObject

from services import DataEditorService


class DatabaseExportWorker(QObject):
    finished: pyqtSignal = pyqtSignal(bool)
    error: pyqtSignal = pyqtSignal(str)
    progress: pyqtSignal = pyqtSignal(str)

    def __init__(self, data_editor_service: DataEditorService, directory: str):
        super().__init__()
        self.data_editor_service = data_editor_service
        self.directory = directory

    def run(self):
        """Export the database to CSV files using a separate thread."""
        try:
            self.progress.emit("Exporting database to CSV files...")
            success = self.data_editor_service.export_data(self.directory)
            self.progress.emit("Database exported successfully.")
            self.finished.emit(success)
        except Exception as e:
            self.error.emit(f"Error exporting database: {str(e)}")
            self.finished.emit(False)
