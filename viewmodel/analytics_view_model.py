from PyQt6.QtCore import pyqtSignal

from navigation import Screen
from services import DataCleaningService, AnalyticsService
from utils import AnalyticsNotifier
from viewmodel import ViewModel


class AnalyticsViewModel(ViewModel):
    nav_destination_changed: pyqtSignal = pyqtSignal(Screen)
    stats_updated: pyqtSignal = pyqtSignal(dict)
    plots_updated: pyqtSignal = pyqtSignal(dict)
    suggestions_updated: pyqtSignal = pyqtSignal(dict)

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
        self._plots = None
        self._suggestions = None

        # Connect to analytics notifier
        self._notifier.statistics_updated.connect(self.on_statistics_updated)
        self._notifier.plots_updated.connect(self.on_plots_updated)
        self._notifier.suggestions_updated.connect(self.on_suggestions_updated)

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def on_statistics_updated(self, statistics: dict):
        self._statistics = statistics
        self.stats_updated.emit(statistics)

    def on_plots_updated(self, plots: dict):
        self._plots = plots
        self.plots_updated.emit(plots)

    def on_suggestions_updated(self, suggestions: dict):
        self._suggestions = suggestions
        self.suggestions_updated.emit(suggestions)

    def apply_suggestion(self, suggestion: dict):
        # TODO: Implement apply_suggestion
        pass

    def discard_suggestion(self, suggestion: dict):
        # TODO: Implement discard_suggestion
        pass

    def save_stats(self):
        # TODO: Implement save_stats
        pass

    def save_plots(self):
        # TODO: Implement save_plots
        pass
