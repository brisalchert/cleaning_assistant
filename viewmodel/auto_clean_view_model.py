from PyQt6.QtCore import pyqtSignal, QThread

from navigation import Screen
from services import DataCleaningService, AnalyticsService, DatabaseService
from utils import Configuration
from viewmodel import ViewModel
from workers import CleaningWorker, ScriptWorker


class AutoCleanViewModel(ViewModel):
    nav_destination_changed: pyqtSignal = pyqtSignal(Screen)
    tables_loaded: pyqtSignal = pyqtSignal(dict)
    table_changed: pyqtSignal = pyqtSignal(dict)
    cleaning_running_changed: pyqtSignal = pyqtSignal(bool)
    cleaning_finished: pyqtSignal = pyqtSignal(bool)
    cleaning_error: pyqtSignal = pyqtSignal(str)
    progress_updated: pyqtSignal = pyqtSignal(int)
    current_step_changed: pyqtSignal = pyqtSignal(str)
    cleaning_stats_updated: pyqtSignal = pyqtSignal(dict)
    script_finished: pyqtSignal = pyqtSignal(bool)

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
        self.worker = None
        self.worker_thread = None
        self.stats = {}

        # Connect to model updates
        self.database_service.model.data_changed.connect(lambda database: self.tables_loaded.emit(database))

        # Initialize configurations
        self.init_cleaning_config()
        self.init_analytics_config()

    def set_table(self, table_name: str):
        self._table = self.data_cleaning_service.set_and_retrieve_table(table_name)
        self.analytics_service.set_table(table_name)
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

    def init_cleaning_stats(self):
        self.stats = {
            "operations": 0,
            "data_types": 0,
            "duplicates": 0,
            "outliers": 0,
            "missing_dropped": 0,
            "missing_imputed": 0
        }
        self.cleaning_stats_updated.emit(self.stats)

    def update_stats(self, key: str, value: int):
        if key in self.stats.keys():
            self.stats[key] += value
            self.cleaning_stats_updated.emit(self.stats)

    def start_worker(self, on_finished, error_signal=None, progress_signal=None, step_signal=None):
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # Reset stats
        self.init_cleaning_stats()
        self.analytics_service.reset_analytics()

        # Connect signals and slots
        self.worker.finished.connect(on_finished)
        if error_signal:
            self.worker.error.connect(error_signal.emit)
        if progress_signal:
            self.worker.progress.connect(progress_signal.emit)
        if step_signal:
            self.worker.step.connect(step_signal.emit)

        # Connect cleaning stats signals
        if step_signal:
            self.worker.cleaning_operations.connect(lambda x: self.update_stats("operations", x))
            self.worker.data_types_converted.connect(lambda x: self.update_stats("data_types", x))
            self.worker.duplicates_removed.connect(lambda x: self.update_stats("duplicates", x))
            self.worker.outliers_removed.connect(lambda x: self.update_stats("outliers", x))
            self.worker.missing_values_dropped.connect(lambda x: self.update_stats("missing_dropped", x))
            self.worker.missing_values_imputed.connect(lambda x: self.update_stats("missing_imputed", x))

        # Thread cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.worker_thread.deleteLater)

        # Connect thread start to worker task
        self.worker_thread.started.connect(self.worker.run)

        # Start worker thread
        self.worker_thread.start()

    def run_current_config(self):
        self._cleaning_running = True
        self.cleaning_running_changed.emit(self._cleaning_running)

        self.worker = CleaningWorker(self.data_cleaning_service, self.analytics_service, self._cleaning_config, self._analytics_config)
        self.start_worker(self.on_run_finished, self.cleaning_error, self.progress_updated, self.current_step_changed)

    def on_run_finished(self, success: bool):
        self._cleaning_running = False
        self.cleaning_running_changed.emit(self._cleaning_running)
        self.cleaning_finished.emit(success)

    def run_script_from_file(self, script_path: str):
        self.worker = ScriptWorker(self.data_cleaning_service, script_path)
        self.start_worker(self.on_script_finished)

    def on_script_finished(self, success: bool):
        self.script_finished.emit(success)

    def save_config_to_file(self, file_path: str):
        self.data_cleaning_service.save_cleaning_script(file_path)
