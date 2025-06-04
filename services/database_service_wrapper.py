from PyQt6.QtCore import QObject, pyqtSignal
from model import DataModel
from services import DatabaseService


class DatabaseServiceWrapper(QObject):
    tables_loaded: pyqtSignal = pyqtSignal(dict)

    def __init__(self, model: DataModel):
        super().__init__()
        self.database_service = DatabaseService(model)

    def load_from_database(self, connection_details: dict) -> bool:
        success = self.database_service.load_from_database(connection_details)
        tables = self.database_service.get_tables()
        self.tables_loaded.emit(tables)

        return success

    def load_from_files(self, file_list: list[str], csv_config: dict) -> bool:
        success = self.database_service.load_from_files(file_list, csv_config)
        tables = self.database_service.get_tables()
        self.tables_loaded.emit(tables)

        return success
