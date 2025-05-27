import io
from PyQt6.QtCore import pyqtSignal
from navigation import Screen
from services import DataCleaningService, AnalyticsService
from viewmodel import ViewModel


class AutoCleanViewModel(ViewModel):
    nav_destination_changed: pyqtSignal = pyqtSignal(Screen)
    cleaning_config_changed: pyqtSignal = pyqtSignal(dict)
    analytics_config_changed: pyqtSignal = pyqtSignal(dict)
    cleaning_running_changed: pyqtSignal = pyqtSignal(bool)
    progress_updated: pyqtSignal = pyqtSignal(float)
    current_step_changed: pyqtSignal = pyqtSignal(str)
    cleaning_stats_updated: pyqtSignal = pyqtSignal(dict)

    def __init__(self, data_cleaning_service: DataCleaningService, analytics_service: AnalyticsService):
        super().__init__()
        self.data_cleaning_service = data_cleaning_service
        self.analytics_service = analytics_service
        self._nav_destination = Screen.AUTO_CLEAN
        self._cleaning_config = None
        self._analytics_config = None
        self._cleaning_running = False
        self._progress = None
        self._current_step = None

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def set_cleaning_config(self, cleaning_config: dict):
        self._cleaning_config = cleaning_config
        self.cleaning_config_changed.emit(cleaning_config)

    def set_analytics_config(self, analytics_config: dict):
        self._analytics_config = analytics_config
        self.analytics_service.set_analytics_config(analytics_config)
        self.analytics_config_changed.emit(analytics_config)

    def run_current_config(self):
        # TODO: Implement run_current_config
        pass

    def load_script_from_file(self, script: io.TextIOWrapper):
        # TODO: Implement load_script_from_file
        pass

    def save_config_to_file(self):
        # TODO: Implement save_config_to_file
        pass
