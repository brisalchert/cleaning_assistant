from PyQt6.QtWidgets import QWidget
from navigation import NavigationController
from view.AbstractView import AbstractView
from viewmodel import AnalyticsViewModel


class AnalyticsView(QWidget, AbstractView):
    @property
    def view_model(self):
        return self._view_model

    @property
    def nav_controller(self):
        return self._nav_controller

    def __init__(self, view_model: AnalyticsViewModel, nav_controller: NavigationController):
        super().__init__()
        self._view_model = view_model
        self._nav_controller = nav_controller
        self.stats: dict = {}
        self.plots: dict = {}
        self.suggestions: dict = {}

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.stats_updated.connect(self.update_stats)
        self._view_model.plots_updated.connect(self.update_plots)
        self._view_model.suggestions_updated.connect(self.update_suggestions)

    def update_stats(self, stats: dict):
        self.stats = stats

    def update_plots(self, plots: dict):
        self.plots = plots

    def update_suggestions(self, suggestions: dict):
        self.suggestions = suggestions

    def export_plot(self, plot_name: str):
        # TODO: Implement export_plot
        pass
