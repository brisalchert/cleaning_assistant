import pandas as pd
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QComboBox, QHBoxLayout, \
    QButtonGroup, QRadioButton, QCheckBox, QPushButton, QProgressBar, QSplitter
from pandas import DataFrame

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
        self.table_name: str = ""
        self.table: DataFrame = pd.DataFrame()
        self.cleaning_column_config_map: dict = {}
        self.analytics_column_config_map: dict = {}
        self.cleaning_config: dict = {}
        self.analytics_config: dict = {}
        self.cleaning_running: bool = False
        self.progress: float = 0
        self.current_step: str = ""
        self.cleaning_stats: dict = {}

        # Set up scroll area for configuration options
        self.configuration_container = QWidget()
        self.configuration_container.setLayout(QVBoxLayout())
        self.configuration_container.layout().setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        configuration_scroll_area = QScrollArea()
        configuration_scroll_area.setWidget(self.configuration_container)
        configuration_scroll_area.setWidgetResizable(True)
        configuration_scroll_area.setMinimumWidth(500)
        configuration_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.configuration_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Set up scroll area for cleaning statistics
        self.statistics_container = QWidget()
        self.statistics_container.setLayout(QVBoxLayout())
        statistics_scroll_area = QScrollArea()
        statistics_scroll_area.setWidget(self.statistics_container)
        statistics_scroll_area.setWidgetResizable(True)
        statistics_scroll_area.setMinimumWidth(300)
        statistics_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.statistics_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Group scroll areas with splitter
        self.splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.splitter.addWidget(configuration_scroll_area)
        self.splitter.addWidget(statistics_scroll_area)
        self.splitter.setSizes([900, 300])
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setHandleWidth(5)

        # Set up view header
        self.header_label = QLabel("Auto-Cleaning Configuration")
        self.header_label.setFont(QFont(self.font, 24))

        # Table selection
        self.table_select_label = QLabel("Select a table for auto-cleaning: ")
        self.table_select_label.setFont(QFont(self.font, 14))
        self.table_select = QComboBox()
        self.table_select.setFont(QFont(self.font, 12))
        self.table_select.currentIndexChanged.connect(lambda: self._view_model.set_table(self.table_select.currentText()))
        self.table_select_container = QWidget()
        self.table_select_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.table_select_container.setLayout(QHBoxLayout())
        self.table_select_container.layout().addWidget(self.table_select_label)
        self.table_select_container.layout().addWidget(self.table_select)
        self.configuration_container.layout().addWidget(self.table_select_container)

        # ----------------------------------------------------------------------
        # --- Cleaning configuration ---
        # ----------------------------------------------------------------------

        self.cleaning_config_container = QWidget()
        self.cleaning_config_container.setLayout(QVBoxLayout())
        self.cleaning_config_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        # Configuration Header
        self.cleaning_config_header = QLabel("Cleaning Configuration:")
        self.cleaning_config_header.setFont(QFont(self.font, 14))
        self.cleaning_config_container.layout().addWidget(self.cleaning_config_header)

        # TODO: Connect buttons to config changes
        # Column-specific options
        # TODO: Add category selection, numerical ranges, string length limits
        self.cleaning_column_options_label = QLabel("Column Options:")
        self.cleaning_column_options_label.setFont(QFont(self.font, 12))
        self.cleaning_column_config_container = QWidget()
        self.cleaning_column_config_container.setLayout(QVBoxLayout())
        self.cleaning_config_container.layout().addWidget(self.cleaning_column_options_label)
        self.cleaning_config_container.layout().addWidget(self.cleaning_column_config_container)

        # Uniqueness Constraints
        self.uniqueness_label = QLabel("Uniqueness Constraints:")
        self.uniqueness_label.setFont(QFont(self.font, 12))
        self.delete_duplicates_checkbox = QCheckBox("Delete exact duplicates")
        self.delete_duplicates_checkbox.setFont(QFont(self.font, 10))
        self.merge_duplicates_checkbox = QCheckBox("Merge almost exact duplicates")
        self.merge_duplicates_checkbox.setFont(QFont(self.font, 10))
        self.cleaning_config_container.layout().addWidget(self.uniqueness_label)
        self.cleaning_config_container.layout().addWidget(self.delete_duplicates_checkbox)
        self.cleaning_config_container.layout().addWidget(self.merge_duplicates_checkbox)

        # Missing Values
        self.missingness_label = QLabel("Missing values:")
        self.missingness_label.setFont(QFont(self.font, 12))
        self.drop_missing_button = QRadioButton("Drop missing values")
        self.drop_missing_button.setFont(QFont(self.font, 10))
        self.impute_missing_button = QRadioButton("Impute missing values")
        self.impute_missing_button.setFont(QFont(self.font, 10))
        self.leave_missing_button = QRadioButton("Do not modify missing values")
        self.leave_missing_button.setFont(QFont(self.font, 10))
        self.missingness_button_group = QButtonGroup()
        self.missingness_button_group.addButton(self.drop_missing_button)
        self.missingness_button_group.addButton(self.impute_missing_button)
        self.missingness_button_group.addButton(self.leave_missing_button)
        self.missingness_button_group.setExclusive(True)
        self.leave_missing_button.setChecked(True)
        self.cleaning_config_container.layout().addWidget(self.missingness_label)
        self.cleaning_config_container.layout().addWidget(self.drop_missing_button)
        self.cleaning_config_container.layout().addWidget(self.impute_missing_button)
        self.cleaning_config_container.layout().addWidget(self.leave_missing_button)

        # Run button and progress bar
        self.run_button = QPushButton("Run Current Configuration")
        self.run_button.setFont(QFont(self.font, 12))
        self.progress_bar_label = QLabel("Waiting to run...")
        self.progress_bar_label.setFont(QFont(self.font, 10))
        self.progress_bar = QProgressBar()
        self.progress_bar.setFont(QFont(self.font, 12))
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.cleaning_config_container.layout().addStretch()
        self.cleaning_config_container.layout().addWidget(self.run_button)
        self.cleaning_config_container.layout().addWidget(self.progress_bar_label)
        self.cleaning_config_container.layout().addWidget(self.progress_bar)

        # ----------------------------------------------------------------------
        # --- Analytics Configuration ---
        # ----------------------------------------------------------------------

        self.analytics_config_container = QWidget()
        self.analytics_config_container.setLayout(QVBoxLayout())
        self.analytics_config_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        # Configuration Header
        self.analytics_config_header = QLabel("Analytics Configuration:")
        self.analytics_config_header.setFont(QFont(self.font, 14))
        self.analytics_config_container.layout().addWidget(self.analytics_config_header)

        # Column-specific options
        self.analytics_column_options_label = QLabel("Column Options:")
        self.analytics_column_options_label.setFont(QFont(self.font, 12))
        self.analytics_column_config_container = QWidget()
        self.analytics_column_config_container.setLayout(QVBoxLayout())
        self.analytics_column_config_container.layout().setSpacing(0)
        self.analytics_config_container.layout().addWidget(self.analytics_column_options_label)
        self.analytics_config_container.layout().addWidget(self.analytics_column_config_container)

        # Categorical values
        self.category_analysis_label = QLabel("Category Analysis:")
        self.category_analysis_label.setFont(QFont(self.font, 12))
        self.category_analysis_checkbox = QCheckBox("Analyze category consistency")
        self.category_analysis_checkbox.setFont(QFont(self.font, 10))
        self.analytics_config_container.layout().addWidget(self.category_analysis_label)
        self.analytics_config_container.layout().addWidget(self.category_analysis_checkbox)

        # Unit uniformity for numerical values
        self.unit_uniformity_label = QLabel("Unit Uniformity:")
        self.unit_uniformity_label.setFont(QFont(self.font, 12))
        self.unit_uniformity_checkbox = QCheckBox("Analyze unit uniformity")
        self.unit_uniformity_checkbox.setFont(QFont(self.font, 10))
        self.analytics_config_container.layout().addWidget(self.unit_uniformity_label)
        self.analytics_config_container.layout().addWidget(self.unit_uniformity_checkbox)

        self.analytics_config_container.layout().addStretch()

        # ----------------------------------------------------------------------
        # Set up layout
        # ----------------------------------------------------------------------

        # Cleaning/Analytics Configuration Layout
        self.configuration_split = QWidget()
        self.configuration_split.setLayout(QHBoxLayout())
        self.configuration_split.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.configuration_split.layout().addWidget(self.cleaning_config_container)
        self.configuration_split.layout().addWidget(self.analytics_config_container)
        self.configuration_split.layout().addStretch()
        self.configuration_container.layout().addWidget(self.configuration_split)

        # Navigation
        self.setup_navigation()

        # Main Layout
        self.auto_clean_layout = QVBoxLayout()
        self.auto_clean_layout.addWidget(self._nav_bar)
        self.auto_clean_layout.addWidget(self.header_label)
        self.auto_clean_layout.addWidget(self.splitter)

        # ----------------------------------------------------------------------
        # --- Initialize UI ---
        # ----------------------------------------------------------------------

        # Initialize UI with the layout
        self.setLayout(self.auto_clean_layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.tables_loaded.connect(self.update_table_select)
        self._view_model.table_changed.connect(self.update_column_options)
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

    def update_table_select(self, tables: dict):
        self.table_select.clear()
        self.table_select.addItems(tables.keys())
        self.table_select.updateGeometry()

    @QtCore.pyqtSlot(dict)
    def update_column_options(self, table: dict):
        self.table_name, self.table = next(iter(table.items()))

        # Update cleaning layout
        cleaning_layout = self.cleaning_column_config_container.layout()

        # Clear existing column config layout
        for i in range(cleaning_layout.count()):
            widget = cleaning_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Clear column config map
        self.cleaning_column_config_map.clear()

        # Set up layout for columns in current table
        for column in self.table.columns:
            cleaning_layout.addWidget(self.create_cleaning_column_config_widget(column))

        # Update analytics layout
        analytics_layout = self.analytics_column_config_container.layout()

        # Clear existing column config layout
        for i in range(analytics_layout.count()):
            widget = analytics_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Clear column config map
        self.analytics_column_config_map.clear()

        # Set up layout for columns in current table
        for column in self.table.columns:
            analytics_layout.addWidget(self.create_analytics_column_config_widget(column))

    def create_cleaning_column_config_widget(self, column_name: str) -> QWidget:
        # Create row with dropdown for column data type
        column_name_label = QLabel(f"{column_name} data type: ")
        column_name_label.setFont(QFont(self.font, 10))

        data_type_select = QComboBox()
        data_type_select.setFont(QFont(self.font, 10))
        data_type_select.addItem("int")
        data_type_select.addItem("float")
        data_type_select.addItem("string")
        data_type_select.addItem("datetime")
        data_type_select.addItem("category")

        container = QWidget()
        container.setLayout(QHBoxLayout())
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        container.layout().addWidget(column_name_label)
        container.layout().addStretch()
        container.layout().addWidget(data_type_select)

        # Map column name to its data type selector
        self.cleaning_column_config_map[column_name] = data_type_select

        # TODO: Connect selector to changes in cleaning config

        return container

    def create_analytics_column_config_widget(self, column_name: str) -> QWidget:
        # Create row with checkboxes for analytics options
        column_name_label = QLabel(f"{column_name}:")
        column_name_label.setFont(QFont(self.font, 10))

        distribution_plot_checkbox = QCheckBox("Analyze data distribution")
        distribution_plot_checkbox.setFont(QFont(self.font, 10))

        missingness_plot_checkbox = QCheckBox("Analyze missingness pattern")
        missingness_plot_checkbox.setFont(QFont(self.font, 10))

        outlier_plot_checkbox = QCheckBox("Analyze outliers")
        outlier_plot_checkbox.setFont(QFont(self.font, 10))

        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        container.layout().addWidget(column_name_label)
        container.layout().addWidget(distribution_plot_checkbox)
        container.layout().addWidget(missingness_plot_checkbox)
        container.layout().addWidget(outlier_plot_checkbox)

        # Map column name to analytics options
        self.analytics_column_config_map[column_name] = [
            distribution_plot_checkbox,
            missingness_plot_checkbox,
            outlier_plot_checkbox
        ]

        # TODO: Connect options to changes in analytics config

        return container

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
