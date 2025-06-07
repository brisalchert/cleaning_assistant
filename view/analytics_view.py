from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QLabel, QPushButton, QHBoxLayout

from navigation import NavigationController
from view import AbstractView
from viewmodel import AnalyticsViewModel


class AnalyticsView(AbstractView):
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

        # Set up view header
        self.header_label = QLabel("Cleaning Analytics")
        self.header_label.setFont(QFont(self.font, 24))
        self.header_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.stats_export_button = QPushButton("Save Statistics")
        self.stats_export_button.setFont(QFont(self.font, 14))
        self.stats_export_button.setEnabled(False)
        self.stats_export_button.clicked.connect(self.export_stats)
        self.plots_export_button = QPushButton("Save Plots")
        self.plots_export_button.setFont(QFont(self.font, 14))
        self.plots_export_button.setEnabled(False)
        self.plots_export_button.clicked.connect(self.export_plots)

        self.header_group = QWidget()
        self.header_group.setLayout(QHBoxLayout())
        self.header_group.layout().addWidget(self.header_label)
        self.header_group.layout().addStretch()
        self.header_group.layout().addWidget(self.stats_export_button)
        self.header_group.layout().addWidget(self.plots_export_button)

        # Set up scroll area for analytics
        self.analytics_container = QWidget()
        self.analytics_container.setLayout(QVBoxLayout())
        self.analytics_container.layout().setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        analytics_scroll_area = QScrollArea()
        analytics_scroll_area.setWidget(self.analytics_container)
        analytics_scroll_area.setWidgetResizable(True)
        analytics_scroll_area.setMinimumWidth(1200)
        analytics_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.analytics_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Navigation
        self.setup_navigation()

        # Main Layout
        self.analytics_layout = QVBoxLayout()
        self.analytics_layout.addWidget(self._nav_bar)
        self.analytics_layout.addWidget(self.header_group)
        self.analytics_layout.addWidget(analytics_scroll_area)

        # ----------------------------------------------------------------------
        # --- Initialize UI ---
        # ----------------------------------------------------------------------

        # Initialize UI with the layout
        self.setLayout(self.analytics_layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.stats_updated.connect(self.update_stats)
        self._view_model.plots_updated.connect(self.update_plots)
        self._view_model.suggestions_updated.connect(self.update_suggestions)

        # Connect navigation controller to UI
        self._nav_controller.nav_destination_changed.connect(self.update_nav_bar)

    def setup_navigation(self):
        super().setup_navigation()
        self._nav_analytics.setChecked(True)

    def update_stats(self, stats: dict):
        self.stats = stats

    def update_plots(self, plots: dict):
        self.plots = plots

    def update_suggestions(self, suggestions: dict):
        self.suggestions = suggestions

    def export_stats(self):
        # TODO: Implement export_stats
        pass

    def export_plots(self, plot_name: str):
        # TODO: Implement export_plots
        pass
