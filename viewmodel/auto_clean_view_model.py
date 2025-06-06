import io
from PyQt6.QtCore import pyqtSignal
from navigation import Screen
from services import DataCleaningService, AnalyticsService, DatabaseService
from utils import Configuration
from viewmodel import ViewModel


class AutoCleanViewModel(ViewModel):
    nav_destination_changed: pyqtSignal = pyqtSignal(Screen)
    tables_loaded: pyqtSignal = pyqtSignal(dict)
    table_changed: pyqtSignal = pyqtSignal(dict)
    cleaning_config_changed: pyqtSignal = pyqtSignal(dict)
    analytics_config_changed: pyqtSignal = pyqtSignal(dict)
    cleaning_running_changed: pyqtSignal = pyqtSignal(bool)
    progress_updated: pyqtSignal = pyqtSignal(float)
    current_step_changed: pyqtSignal = pyqtSignal(str)
    cleaning_stats_updated: pyqtSignal = pyqtSignal(dict)

    def __init__(self, database_service: DatabaseService, data_cleaning_service: DataCleaningService, analytics_service: AnalyticsService):
        super().__init__()
        self.database_service = database_service
        self.data_cleaning_service = data_cleaning_service
        self.analytics_service = analytics_service
        self._nav_destination = Screen.AUTO_CLEAN
        self._table = None
        self._cleaning_config = None
        self._analytics_config = None
        self._cleaning_running = False
        self._progress = None
        self._current_step = None

        # Connect to model updates
        self.database_service.model.observe(self.tables_loaded.emit)

        # Initialize configurations
        self.init_cleaning_config()
        self.init_analytics_config()

    def set_table(self, table_name: str):
        self._table = self.data_cleaning_service.set_and_retrieve_table(table_name)
        self.table_changed.emit(self._table)

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def set_cleaning_config(self, key: Configuration, value, column: str = None):
        if column:
            # Create dictionary for column if not present
            if not column in self._cleaning_config[Configuration.COLUMNS]:
                self._cleaning_config[Configuration.COLUMNS][column] = {}

            self._cleaning_config[Configuration.COLUMNS][column][key] = value
        else:
            self._cleaning_config[key] = value

        self.cleaning_config_changed.emit(self._cleaning_config)

    def set_analytics_config(self, key: Configuration, value, column: str = None):
        if column:
            # Create dictionary for column if not present
            if not column in self._analytics_config[Configuration.COLUMNS]:
                self._analytics_config[Configuration.COLUMNS][column] = {}

            self._analytics_config[Configuration.COLUMNS][column][key] = value
        else:
            self._analytics_config[key] = value

        # Update config in the analytics service
        self.analytics_service.set_analytics_config(self._analytics_config)
        self.analytics_config_changed.emit(self._analytics_config)

    def init_cleaning_config(self):
        self._cleaning_config = {
            Configuration.COLUMNS: {},
            Configuration.DELETE_DUPLICATES: False,
            Configuration.DROP_MISSING: False,
            Configuration.IMPUTE_MISSING_MEAN: False,
            Configuration.IMPUTE_MISSING_MEDIAN: False
        }

    def init_analytics_config(self):
        self._analytics_config = {
            Configuration.COLUMNS: {},
            Configuration.ANALYZE_MISSINGNESS: False,
            Configuration.ANALYZE_CATEGORIES: False,
            Configuration.ANALYZE_UNITS: False
        }

    def run_current_config(self):
        # TODO: Implement run_current_config
        pass

    def load_script_from_file(self, script: io.TextIOWrapper):
        # TODO: Implement load_script_from_file
        pass

    def save_config_to_file(self):
        # TODO: Implement save_config_to_file
        pass
