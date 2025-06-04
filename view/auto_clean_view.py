from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QComboBox, QHBoxLayout
from navigation import NavigationController
from view import AbstractView
from viewmodel import AutoCleanViewModel


class AutoCleanView(AbstractView):
    @property
    def view_model(self):
        return self._view_model

    @property
    def nav_controller(self):
        return self._nav_controller

    def __init__(self, view_model: AutoCleanViewModel, nav_controller: NavigationController):
        super().__init__()
        self._view_model = view_model
        self._nav_controller = nav_controller
        self.table = None
        self.cleaning_config: dict = {}
        self.analytics_config: dict = {}
        self.cleaning_running: bool = False
        self.progress: float = 0
        self.current_step: str = ""
        self.cleaning_stats: dict = {}

        # Set up scroll area for configuration options
        self.configuration_container = QWidget()
        self.configuration_container.setLayout(QVBoxLayout())
        self.configuration_container.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)
        configuration_scroll_area = QScrollArea()
        configuration_scroll_area.setWidget(self.configuration_container)
        configuration_scroll_area.setWidgetResizable(True)
        configuration_scroll_area.setMinimumWidth(500)
        configuration_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.configuration_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Set up view header
        self.header_label = QLabel("Auto-Cleaning Configuration")
        self.header_label.setFont(QFont(self.font, 24))

        # Table selection
        self.table_select_label = QLabel("Select a table for auto-cleaning: ")
        self.table_select = QComboBox()
        self.table_select.setFont(QFont(self.font, 12))
        self.table_select.currentIndexChanged.connect(lambda: self.set_table(self.table_select.currentText()))
        self.table_select_container = QWidget()
        self.table_select_container.setLayout(QHBoxLayout())
        self.table_select_container.layout().addWidget(self.table_select_label)
        self.table_select_container.layout().addWidget(self.table_select)
        self.configuration_container.layout().addWidget(self.table_select_container)

        # Cleaning configuration
        self.cleaning_config_container = QWidget()
        self.cleaning_config_container.setLayout(QVBoxLayout())
        self.configuration_container.layout().addWidget(self.cleaning_config_container)

        # Navigation
        self.setup_navigation()

        # Main Layout
        self.auto_clean_layout = QVBoxLayout()
        self.auto_clean_layout.addWidget(self._nav_bar)
        self.auto_clean_layout.addWidget(self.header_label)
        self.auto_clean_layout.addWidget(configuration_scroll_area)

        # ----------------------------------------------------------------------
        # --- Initialize UI ---
        # ----------------------------------------------------------------------

        # Initialize UI with the layout
        self.setLayout(self.auto_clean_layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.tables_loaded.connect(self.update_table_select)
        self._view_model.cleaning_config_changed.connect(self.update_cleaning_config)
        self._view_model.analytics_config_changed.connect(self.update_analytics_config)
        self._view_model.cleaning_running_changed.connect(self.update_running)
        self._view_model.progress_updated.connect(self.update_progress)
        self._view_model.current_step_changed.connect(self.update_step)
        self._view_model.cleaning_stats_updated.connect(self.update_stats)

        # Connect navigation controller to UI
        self._nav_controller.nav_destination_changed.connect(self.update_nav_bar)

    def setup_navigation(self):
        super().setup_navigation()
        self._nav_auto_clean.setChecked(True)

    def set_table(self, table_name: str):
        self.table = self._view_model.set_table(table_name)

    def update_table_select(self, tables: dict):
        self.table_select.clear()
        self.table_select.addItems(tables.keys())

    def update_cleaning_config(self, cleaning_config: dict):
        self.cleaning_config = cleaning_config

    def update_analytics_config(self, analytics_config: dict):
        self.analytics_config = analytics_config

    def update_running(self, running: bool):
        self.cleaning_running = running

    def update_progress(self, progress: float):
        self.progress = progress

    def update_step(self, step: str):
        self.current_step = step

    def update_stats(self, stats: dict):
        self.cleaning_stats = stats
