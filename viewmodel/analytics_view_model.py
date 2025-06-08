import json
from pathlib import Path

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
    suggestion_result: pyqtSignal = pyqtSignal(bool)
    suggestion_error: pyqtSignal = pyqtSignal(str)

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
        self.statistics = None
        self.plot_data = None
        self.suggestions = None

        # Connect to analytics notifier
        self._notifier.statistics_updated.connect(self.on_statistics_updated)
        self._notifier.plots_updated.connect(self.on_plot_data_updated)
        self._notifier.suggestions_updated.connect(self.on_suggestions_updated)
        self._notifier.analytics_updated.connect(self.on_analytics_updated)

    def set_nav_destination(self, destination: Screen):
        self._nav_destination = destination
        self.nav_destination_changed.emit(destination)

    def on_statistics_updated(self, statistics: dict):
        self.statistics = statistics
        self.stats_updated.emit(statistics)

    def on_plot_data_updated(self, plot_data: dict):
        self.plot_data = plot_data
        self.plot_data_updated.emit(plot_data)

    def on_suggestions_updated(self, suggestions: dict):
        self.suggestions = suggestions
        self.suggestions_updated.emit(suggestions)

    def on_analytics_updated(self, available: bool):
        self.analytics_updated.emit(available)

    def apply_suggestion(
            self,
            operation: Operation,
            column: str,
            category_map=None
    ):
        try:
            if operation == Operation.DROP_MISSING:
                self.data_cleaning_service.drop_missing(column)
            elif operation == Operation.IMPUTE_MEAN:
                self.data_cleaning_service.impute_missing_mean(column)
            elif operation == Operation.IMPUTE_MEDIAN:
                self.data_cleaning_service.impute_missing_median(column)
            elif operation == Operation.IMPUTE_MODE:
                self.data_cleaning_service.impute_missing_mode(column)
            elif operation == Operation.DROP_UPPER:
                self.data_cleaning_service.drop_standard_outliers(column, upper=True)
            elif operation == Operation.DROP_LOWER:
                self.data_cleaning_service.drop_standard_outliers(column, lower=True)
            elif operation == Operation.STANDARDIZE:
                self.data_cleaning_service.standardize(column)
            elif operation == Operation.CORRECT_CATEGORIES and category_map is not None:
                self.data_cleaning_service.clean_categories(column, category_map)
            else:
                raise ValueError('Invalid operation')

            self.suggestion_result.emit(True)
        except Exception as e:
            self.suggestion_result.emit(False)
            self.suggestion_error.emit(str(e))

    def save_stats(self, directory: str):
        filename = "cleaning_statistics.json"
        file_path = Path(f"{directory}/{filename}")

        with open(file_path, "w") as file:
            json.dump(self.statistics, file, indent=4)

    def save_plots(self, directory: str, missing_plot=None, outlier_plot=None, distribution_plots=None):
        path = Path(f"{directory}/cleaning_assistant_plots")
        path.mkdir(parents=True, exist_ok=True)

        if missing_plot:
            file_path = Path(f"{path}/missingness.png")
            missing_plot.fig.savefig(file_path)

        if outlier_plot:
            file_path = Path(f"{path}/outliers.png")
            outlier_plot.fig.savefig(file_path)

        if distribution_plots:
            for column, plot in distribution_plots.items():
                file_path = Path(f"{path}/{column}_distribution.png")
                plot.fig.savefig(file_path)
