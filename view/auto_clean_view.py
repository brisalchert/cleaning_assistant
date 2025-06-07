import pandas as pd
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QComboBox, QHBoxLayout, \
    QButtonGroup, QRadioButton, QCheckBox, QPushButton, QProgressBar, QSplitter, QFrame, QStackedWidget, QLineEdit, \
    QDateEdit, QTextEdit, QMessageBox, QFileDialog
from pandas import DataFrame

from navigation import NavigationController
from utils import Configuration
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
        self.cleaning_stats: dict = {}
        self.cleaning_running = None
        self.script_message_box = None

        # Set up scroll area for configuration options
        self.configuration_container = QWidget()
        self.configuration_container.setLayout(QVBoxLayout())
        self.configuration_container.layout().setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        configuration_scroll_area = QScrollArea()
        configuration_scroll_area.setWidget(self.configuration_container)
        configuration_scroll_area.setWidgetResizable(True)
        configuration_scroll_area.setMinimumWidth(900)
        configuration_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.configuration_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Run button and progress bar
        self.run_button = QPushButton("Run Current Configuration")
        self.run_button.setFont(QFont(self.font, 12))
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self._view_model.run_current_config)
        self.progress_bar_label = QLabel("Waiting to run...")
        self.progress_bar_label.setFont(QFont(self.font, 10))
        self.progress_bar = QProgressBar()
        self.progress_bar.setFont(QFont(self.font, 12))
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Place run button below configuration scroll area
        self.run_container = QWidget()
        self.run_container.setLayout(QVBoxLayout())
        self.run_container.layout().addWidget(configuration_scroll_area)
        self.run_container.layout().addWidget(self.run_button)
        self.run_container.layout().addWidget(self.progress_bar_label)
        self.run_container.layout().addWidget(self.progress_bar)

        # Set up scroll area for cleaning statistics
        self.statistics_container = QWidget()
        self.statistics_container.setLayout(QVBoxLayout())
        statistics_scroll_area = QScrollArea()
        statistics_scroll_area.setWidget(self.statistics_container)
        statistics_scroll_area.setWidgetResizable(True)
        statistics_scroll_area.setMinimumWidth(300)
        statistics_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.statistics_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Create statistics labels
        self.statistics_label = QLabel("Cleaning Statistics:")
        self.statistics_label.setFont(QFont(self.font, 14))
        self.cleaning_operations_label = QLabel("Total Modifications: 0")
        self.cleaning_operations_label.setFont(QFont(self.font, 12))
        self.data_types_label = QLabel("Data Types Converted: 0")
        self.data_types_label.setFont(QFont(self.font, 12))
        self.duplicates_label = QLabel("Duplicates Removed: 0")
        self.duplicates_label.setFont(QFont(self.font, 12))
        self.outliers_label = QLabel("Outliers Removed: 0")
        self.outliers_label.setFont(QFont(self.font, 12))
        self.values_dropped = QLabel("Missing Values Dropped: 0")
        self.values_dropped.setFont(QFont(self.font, 12))
        self.values_imputed = QLabel("Missing Values Imputed: 0")
        self.values_imputed.setFont(QFont(self.font, 12))

        self.statistics_container.layout().addWidget(self.statistics_label)
        self.statistics_container.layout().addWidget(self.cleaning_operations_label)
        self.statistics_container.layout().addWidget(self.data_types_label)
        self.statistics_container.layout().addWidget(self.duplicates_label)
        self.statistics_container.layout().addWidget(self.outliers_label)
        self.statistics_container.layout().addWidget(self.values_dropped)
        self.statistics_container.layout().addWidget(self.values_imputed)
        self.statistics_container.layout().addStretch()

        # Group scroll areas with splitter
        self.splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.splitter.addWidget(self.run_container)
        self.splitter.addWidget(statistics_scroll_area)
        self.splitter.setSizes([900, 300])
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setHandleWidth(5)

        # Set up view header
        self.header_label = QLabel("Auto-Cleaning Configuration")
        self.header_label.setFont(QFont(self.font, 24))
        self.script_export_button = QPushButton("Export Cleaning Script")
        self.script_export_button.setFont(QFont(self.font, 14))
        self.script_export_button.setEnabled(False)
        self.script_export_button.clicked.connect(self.on_script_export)
        self.load_script_button = QPushButton("Load Cleaning Script")
        self.load_script_button.setFont(QFont(self.font, 14))
        self.load_script_button.clicked.connect(self.on_load_script)

        self.header_group = QWidget()
        self.header_group.setLayout(QHBoxLayout())
        self.header_group.layout().addWidget(self.header_label)
        self.header_group.layout().addStretch()
        self.header_group.layout().addWidget(self.script_export_button)
        self.header_group.layout().addWidget(self.load_script_button)

        # Table selection
        self.table_select_label = QLabel("Select a table for auto-cleaning: ")
        self.table_select_label.setFont(QFont(self.font, 14))
        self.table_select = QComboBox()
        self.table_select.setFont(QFont(self.font, 12))
        self.table_select.currentIndexChanged.connect(self.change_table)
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

        # Column-specific options
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
        self.cleaning_config_container.layout().addWidget(self.uniqueness_label)
        self.cleaning_config_container.layout().addWidget(self.delete_duplicates_checkbox)

        self.bind_cleaning_config_update(
            self.delete_duplicates_checkbox.checkStateChanged,
            Configuration.DELETE_DUPLICATES,
            self.delete_duplicates_checkbox.isChecked,
            update_on_init=True
        )

        # Missing Values
        self.missingness_label = QLabel("Missing values:")
        self.missingness_label.setFont(QFont(self.font, 12))
        self.drop_missing_button = QRadioButton("Drop missing values")
        self.drop_missing_button.setFont(QFont(self.font, 10))
        self.impute_missing_mean_button = QRadioButton("Impute missing values with mean")
        self.impute_missing_mean_button.setFont(QFont(self.font, 10))
        self.impute_missing_median_button = QRadioButton("Impute missing values with median")
        self.impute_missing_median_button.setFont(QFont(self.font, 10))
        self.leave_missing_button = QRadioButton("Do not modify missing values")
        self.leave_missing_button.setFont(QFont(self.font, 10))
        self.missingness_button_group = QButtonGroup()
        self.missingness_button_group.addButton(self.drop_missing_button)
        self.missingness_button_group.addButton(self.impute_missing_mean_button)
        self.missingness_button_group.addButton(self.impute_missing_median_button)
        self.missingness_button_group.addButton(self.leave_missing_button)
        self.missingness_button_group.setExclusive(True)
        self.leave_missing_button.setChecked(True)
        self.cleaning_config_container.layout().addWidget(self.missingness_label)
        self.cleaning_config_container.layout().addWidget(self.drop_missing_button)
        self.cleaning_config_container.layout().addWidget(self.impute_missing_mean_button)
        self.cleaning_config_container.layout().addWidget(self.impute_missing_median_button)
        self.cleaning_config_container.layout().addWidget(self.leave_missing_button)

        self.bind_cleaning_config_update(
            self.drop_missing_button.toggled,
            Configuration.DROP_MISSING,
            self.drop_missing_button.isChecked,
            update_on_init=True,
        )

        self.bind_cleaning_config_update(
            self.impute_missing_mean_button.toggled,
            Configuration.IMPUTE_MISSING_MEAN,
            self.impute_missing_mean_button.isChecked,
            update_on_init=True
        )

        self.bind_cleaning_config_update(
            self.impute_missing_median_button.toggled,
            Configuration.IMPUTE_MISSING_MEDIAN,
            self.impute_missing_median_button.isChecked,
            update_on_init=True
        )

        # Align layout items to the top
        self.cleaning_config_container.layout().addStretch()

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
        self.column_config_hint = QLabel("Note: Distribution analysis is only available for numeric, datetime, or boolean columns.")
        self.column_config_hint.setFont(QFont(self.font, 10))
        self.column_config_hint.setWordWrap(True)
        self.analytics_config_container.layout().addWidget(self.analytics_column_options_label)
        self.analytics_config_container.layout().addWidget(self.column_config_hint)
        self.analytics_config_container.layout().addWidget(self.analytics_column_config_container)

        # Missing values
        self.missingness_analysis_label = QLabel("Missing Values:")
        self.missingness_analysis_label.setFont(QFont(self.font, 12))
        self.missingness_plot_checkbox = QCheckBox("Analyze missingness pattern")
        self.missingness_plot_checkbox.setFont(QFont(self.font, 10))
        self.analytics_config_container.layout().addWidget(self.missingness_analysis_label)
        self.analytics_config_container.layout().addWidget(self.missingness_plot_checkbox)

        self.bind_analysis_config_update(
            self.missingness_plot_checkbox.checkStateChanged,
            Configuration.ANALYZE_MISSINGNESS,
            self.missingness_plot_checkbox.isChecked,
            update_on_init=True
        )

        # Categorical values
        self.category_analysis_label = QLabel("Category Analysis:")
        self.category_analysis_label.setFont(QFont(self.font, 12))
        self.category_analysis_checkbox = QCheckBox("Analyze category consistency")
        self.category_analysis_checkbox.setFont(QFont(self.font, 10))
        self.analytics_config_container.layout().addWidget(self.category_analysis_label)
        self.analytics_config_container.layout().addWidget(self.category_analysis_checkbox)

        self.bind_analysis_config_update(
            self.category_analysis_checkbox.checkStateChanged,
            Configuration.ANALYZE_CATEGORIES,
            self.category_analysis_checkbox.isChecked,
            update_on_init=True
        )

        # Outliers
        self.outlier_analysis_label = QLabel("Outlier Analysis:")
        self.outlier_analysis_label.setFont(QFont(self.font, 12))
        self.outlier_analysis_checkbox = QCheckBox("Analyze outliers")
        self.outlier_analysis_checkbox.setFont(QFont(self.font, 10))
        self.analytics_config_container.layout().addWidget(self.outlier_analysis_label)
        self.analytics_config_container.layout().addWidget(self.outlier_analysis_checkbox)

        self.bind_analysis_config_update(
            self.outlier_analysis_checkbox.checkStateChanged,
            Configuration.ANALYZE_OUTLIERS,
            self.outlier_analysis_checkbox.isChecked,
            update_on_init=True
        )

        # Align layout items to the top
        self.analytics_config_container.layout().addStretch()

        # ----------------------------------------------------------------------
        # Set up layout
        # ----------------------------------------------------------------------

        # Cleaning/Analytics Configuration Layout
        self.configuration_split = QWidget()
        self.configuration_split.setLayout(QHBoxLayout())
        self.configuration_split.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        self.configuration_split.layout().addWidget(self.cleaning_config_container)
        self.configuration_split.layout().addWidget(separator)
        self.configuration_split.layout().addWidget(self.analytics_config_container)
        self.configuration_split.layout().addStretch()
        self.configuration_container.layout().addWidget(self.configuration_split)

        # Navigation
        self.setup_navigation()

        # Main Layout
        self.auto_clean_layout = QVBoxLayout()
        self.auto_clean_layout.addWidget(self._nav_bar)
        self.auto_clean_layout.addWidget(self.header_group)
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
        self._view_model.cleaning_running_changed.connect(self.update_running)
        self._view_model.cleaning_finished.connect(self.on_cleaning_finished)
        self._view_model.cleaning_error.connect(self.show_error_dialog)
        self._view_model.progress_updated.connect(self.update_progress)
        self._view_model.current_step_changed.connect(self.update_step)
        self._view_model.cleaning_stats_updated.connect(self.update_stats)
        self._view_model.script_finished.connect(self.update_script_message_box)

        # Connect navigation controller to UI
        self._nav_controller.nav_destination_changed.connect(self.update_nav_bar)

    def setup_navigation(self):
        super().setup_navigation()
        self._nav_auto_clean.setChecked(True)

    def update_table_select(self, tables: dict):
        self.table_select.clear()

        if tables:
            self.table_select.addItems(tables.keys())
            self.run_button.setEnabled(True)
        else:
            self.run_button.setEnabled(False)

        self.table_select.updateGeometry()

    def change_table(self, table_select_index):
        if not self.cleaning_running:
            self._view_model.init_cleaning_config()
            self._view_model.init_analytics_config()
            self._view_model.set_table(self.table_select.currentText())

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

        # Set up layout for columns in current table
        for column in self.table.columns:
            analytics_layout.addWidget(self.create_analytics_column_config_widget(column))

    def create_cleaning_column_config_widget(self, column_name: str) -> QWidget:
        # Create row with dropdown for column data type
        column_name_label = QLabel(f"\"{column_name}\" data type: ")
        column_name_label.setFont(QFont(self.font, 10))

        data_type_select = QComboBox()
        data_type_select.setFont(QFont(self.font, 10))
        data_type_select.addItem("int64")
        data_type_select.addItem("float64")
        data_type_select.addItem("bool")
        data_type_select.addItem("string")
        data_type_select.addItem("datetime64[ns]")
        data_type_select.addItem("category")
        data_type_select.addItem("object")

        # Set initial data type
        data_type_select.setCurrentText(str(self._view_model.data_cleaning_service.get_data_type(column_name)))

        # Integer range constraints
        int_range_container = QWidget()
        int_range_container.setLayout(QHBoxLayout())
        int_min = self.append_constraints_widget(int_range_container, "Min:", QIntValidator())
        int_max = self.append_constraints_widget(int_range_container, "Max:", QIntValidator())

        # Float range constraints
        float_range_container = QWidget()
        float_range_container.setLayout(QHBoxLayout())
        float_min = self.append_constraints_widget(float_range_container, "Min:", QDoubleValidator())
        float_max = self.append_constraints_widget(float_range_container, "Max:", QDoubleValidator())

        # String length constraints
        string_length_container = QWidget()
        string_length_container.setLayout(QHBoxLayout())
        string_max = self.append_constraints_widget(string_length_container, "Max Character Length:", QIntValidator())

        # Date Constraints
        date_range_container = QWidget()
        date_range_container.setLayout(QHBoxLayout())
        date_min = self.append_date_constraints_widget(date_range_container, "Min:")
        date_max = self.append_date_constraints_widget(date_range_container, "Max:")

        # Category List
        category_names_container = QWidget()
        category_names_container.setLayout(QHBoxLayout())
        categories = self.append_constraints_widget(category_names_container, "Categories:", None)
        category_widget_container = QWidget()
        category_widget_container.setLayout(QVBoxLayout())
        input_hint = QLabel("Separate categories with spaces and no commas.")
        input_hint.setFont(QFont(self.font, 10))
        category_widget_container.layout().addWidget(category_names_container)
        category_widget_container.layout().addWidget(input_hint)

        # Stacked widget for data type cleaning options
        data_type_config_stack = QStackedWidget()
        data_type_config_stack.setLayout(QHBoxLayout())
        data_type_config_stack.layout().addWidget(int_range_container)
        data_type_config_stack.layout().addWidget(float_range_container)
        data_type_config_stack.layout().addWidget(QWidget()) # Empty for "bool" type
        data_type_config_stack.layout().addWidget(string_length_container)
        data_type_config_stack.layout().addWidget(date_range_container)
        data_type_config_stack.layout().addWidget(category_widget_container)
        data_type_config_stack.layout().addWidget(QWidget()) # Empty for "object" type

        # Connect selector to changes in stacked widget display
        data_type_select.currentIndexChanged.connect(data_type_config_stack.setCurrentIndex)
        data_type_config_stack.setCurrentIndex(data_type_select.currentIndex())

        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        container.layout().addWidget(column_name_label)
        container.layout().addWidget(data_type_select)
        container.layout().addWidget(data_type_config_stack)

        # Connect selector signals to cleaning configuration
        self.bind_cleaning_config_update(
            data_type_select.currentIndexChanged,
            Configuration.DATA_TYPE,
            data_type_select.currentText,
            column_name,
            True
        )
        self.bind_cleaning_config_update(
            int_min.textChanged,
            Configuration.INT_MIN,
            int_min.text,
            column_name
        )
        self.bind_cleaning_config_update(
            int_max.textChanged,
            Configuration.INT_MAX,
            int_max.text,
            column_name
        )
        self.bind_cleaning_config_update(
            float_min.textChanged,
            Configuration.FLOAT_MIN,
            float_min.text,
            column_name
        )
        self.bind_cleaning_config_update(
            float_max.textChanged,
            Configuration.FLOAT_MAX,
            float_max.text,
            column_name
        )
        self.bind_cleaning_config_update(
            string_max.textChanged,
            Configuration.STRING_MAX,
            string_max.text,
            column_name
        )
        self.bind_cleaning_config_update(
            date_min.dateChanged,
            Configuration.DATE_MIN,
            date_min.text,
            column_name
        )
        self.bind_cleaning_config_update(
            date_max.dateChanged,
            Configuration.DATE_MAX,
            date_max.text,
            column_name
        )
        self.bind_cleaning_config_update(
            categories.textChanged,
            Configuration.CATEGORIES,
            categories.text,
            column_name
        )

        return container

    def create_analytics_column_config_widget(self, column_name: str) -> QWidget:
        # Create row with checkboxes for analytics options
        column_name_label = QLabel(f"\"{column_name}\":")
        column_name_label.setFont(QFont(self.font, 10))

        distribution_plot_checkbox = QCheckBox("Analyze data distribution")
        distribution_plot_checkbox.setFont(QFont(self.font, 10))

        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        container.layout().addWidget(column_name_label)
        container.layout().addWidget(distribution_plot_checkbox)

        # Connect selector signals to analysis configuration
        self.bind_analysis_config_update(
            distribution_plot_checkbox.checkStateChanged,
            Configuration.ANALYZE_DISTRIBUTION,
            distribution_plot_checkbox.isChecked,
            column_name,
            True
        )

        return container

    def bind_cleaning_config_update(self, signal, config_key, config_value_getter, column=None, update_on_init=False):
        """Binds the signal from a configuration selector to its corresponding
        setting in the cleaning configuration."""
        signal.connect(
            lambda: self._view_model.set_cleaning_config(
                config_key,
                config_value_getter(),
                column=column
            )
        )

        if update_on_init:
            self._view_model.set_cleaning_config(config_key, config_value_getter(), column=column)

    def bind_analysis_config_update(self, signal, config_key, config_value_getter, column=None, update_on_init=False):
        """Binds the signal from a configuration selector to its corresponding
        setting in the analysis configuration."""
        signal.connect(
            lambda: self._view_model.set_analytics_config(
                config_key,
                config_value_getter(),
                column=column
            )
        )

        if update_on_init:
            self._view_model.set_analytics_config(config_key, config_value_getter(), column=column)

    def on_cleaning_finished(self, success: bool):
        self.progress_bar_label.setText("Waiting to run...")
        self.progress_bar.setValue(0)
        self.script_export_button.setEnabled(success)

    def on_script_export(self):
        export_dialog = QFileDialog()
        directory = export_dialog.getExistingDirectory(self, "Select Directory", ".", QFileDialog.Option.ShowDirsOnly)

        if directory:
            self._view_model.save_config_to_file(directory)

    def on_load_script(self):
        load_dialog = QFileDialog()
        script = load_dialog.getOpenFileName(self, "Select Script File", ".")

        if script:
            self.show_script_message_box()
            self._view_model.run_script_from_file(script[0])

    def update_running(self, running: bool):
        if running:
            self.reset_stats()
        self.cleaning_running = running
        self.run_button.setEnabled(not running)

    def update_progress(self, progress: float):
        self.progress_bar.setValue(progress)

    def update_step(self, step: str):
        self.progress_bar_label.setText(step)

    def update_stats(self, stats: dict):
        self.cleaning_operations_label.setText(f"Total Modifications: {stats['operations']}")
        self.data_types_label.setText(f"Data Types Converted: {stats['data_types']}")
        self.duplicates_label.setText(f"Duplicates Removed: {stats['duplicates']}")
        self.outliers_label.setText(f"Outliers Removed: {stats['outliers']}")
        self.values_dropped.setText(f"Missing Values Dropped: {stats['missing_dropped']}")
        self.values_imputed.setText(f"Missing Values Imputed: {stats['missing_imputed']}")

    def reset_stats(self):
        self.cleaning_operations_label.setText("Total Modifications: 0")
        self.data_types_label.setText("Data Types Converted: 0")
        self.duplicates_label.setText("Duplicates Removed: 0")
        self.outliers_label.setText("Outliers Removed: 0")
        self.values_dropped.setText("Missing Values Dropped: 0")
        self.values_imputed.setText("Missing Values Imputed: 0")

    def show_error_dialog(self, error: str):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Cleaning Error")
        error_dialog.setText("There was an error cleaning the data.")
        error_dialog.setInformativeText(error)
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.exec()

    def show_script_message_box(self):
        """Show a message box for script running."""
        self.script_message_box = QMessageBox()
        self.script_message_box.setIcon(QMessageBox.Icon.NoIcon)
        self.script_message_box.setWindowTitle("Running Script")
        self.script_message_box.setText("Running script from loaded file...")
        self.script_message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.script_message_box.button(QMessageBox.StandardButton.Ok).setEnabled(False)
        self.script_message_box.show()

    def update_script_message_box(self, success: bool):
        """Update the script message box based on script execution success."""
        if self.script_message_box:
            if success:
                self.script_message_box.setText("Script execution successful.")
                self.script_message_box.setInformativeText("Output saved to desktop.")
            else:
                self.script_message_box.setIcon(QMessageBox.Icon.Critical)
                self.script_message_box.setText("Script execution failed.")
                self.script_message_box.setInformativeText("Ensure you are loading a script file generated by this application.")
            self.script_message_box.button(QMessageBox.StandardButton.Ok).setEnabled(True)

    def append_constraints_widget(self, container: QWidget, label_text: str, validator = None) -> QLineEdit:
        """Creates and appends a cleaning constraints label and input selector
        to the provided container. Returns the input widget for code access to
        changes and values."""
        label = QLabel(label_text)
        label.setFont(QFont(self.font, 10))
        input_box = QLineEdit()
        input_box.setFont(QFont(self.font, 10))
        if validator:
            input_box.setValidator(validator)

        container.layout().addWidget(label)
        container.layout().addWidget(input_box)

        # Return the input widget
        return input_box

    def append_date_constraints_widget(self, container: QWidget, label_text: str) -> QDateEdit:
        """Creates and appends a cleaning constraints label and input selector
        to the provided container. Returns the input widget for code access to
        changes and values. For use specifically with date fields."""
        label = QLabel(label_text)
        label.setFont(QFont(self.font, 10))
        input_box = QDateEdit()
        input_box.setFont(QFont(self.font, 10))
        input_box.setDisplayFormat("yyyy-MM-dd")

        # Set initial dates
        if label_text == "Min:":
            input_box.setDate(QDate(1900, 1, 1))
        elif label_text == "Max:":
            input_box.setDate(QDate.currentDate())

        container.layout().addWidget(label)
        container.layout().addWidget(input_box)

        # Return the input widget
        return input_box
