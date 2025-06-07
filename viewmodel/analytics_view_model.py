from PyQt6.QtCore import pyqtSignal

from navigation import Screen
from services import DataCleaningService, AnalyticsService
from utils import AnalyticsNotifier, Operation
from viewmodel import ViewModel


class AnalyticsViewModel(ViewModel):
    nav_destination_changed: pyqtSignal = pyqtSignal(Screen)
    stats_updated: pyqtSignal = pyqtSignal(dict)
    plot_data_updated: pyqtSignal = pyqtSignal(dict)
    suggestions_updated: pyqtSignal = pyqtSignal(dict)
    analytics_updated: pyqtSignal = pyqtSignal(bool)

    def __init__(
            self,
            data_cleaning_service: DataCleaningService,
            analytics_service: AnalyticsService,
            analytics_notifier: AnalyticsNotifier
    ):
        super().__init__()
        self.data_cleaning_service = data_cleaning_service
        self.analytics_service = analytics_service
        self._notifier = analytics_notifier
        self._nav_destination = Screen.ANALYTICS
        self._statistics = None
        self._plot_data = None
        self._suggestions = None

        # Connect to analytics notifier
        self._notifier.statistics_updated.connect(self.on_statistics_updated)
        self._notifier.plots_updated.connect(self.on_plot_data_updated)
        self._notifier.suggestions_updated.connect(self.on_suggestions_updated)
        self._notifier.analytics_updated.connect(self.on_analytics_updated)

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def on_statistics_updated(self, statistics: dict):
        self._statistics = statistics
        self.stats_updated.emit(statistics)

    def on_plot_data_updated(self, plot_data: dict):
        self._plot_data = plot_data
        self.plot_data_updated.emit(plot_data)

    def on_suggestions_updated(self, suggestions: dict):
        self._suggestions = suggestions
        self.suggestions_updated.emit(suggestions)

    def on_analytics_updated(self, available: bool):
        self.analytics_updated.emit(available)

    def apply_suggestion(self, operation: Operation, column: str):
        # TODO: Implement apply_suggestion
        pass

    def save_stats(self):
        # TODO: Implement save_stats
        pass

    def save_plots(self):
        # TODO: Implement save_plots
        pass
