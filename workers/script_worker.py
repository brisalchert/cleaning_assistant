from PyQt6.QtCore import QObject, pyqtSignal

from services import DataCleaningService


class ScriptWorker(QObject):
    finished: pyqtSignal = pyqtSignal(bool)

    def __init__(self, data_cleaning_service: DataCleaningService, script_path: str):
        super().__init__()
        self.data_cleaning_service = data_cleaning_service
        self.script_path = script_path

    def run(self):
        success = self.data_cleaning_service.apply_cleaning_script(self.script_path)
        self.finished.emit(success)
