from functools import partial

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTableView, QVBoxLayout, QWidget, QScrollArea, QLabel, QSizePolicy, QSplitter, \
    QPushButton, QHBoxLayout, QDialog, QMessageBox, QFileDialog
from pandas import DataFrame

from model import DataFrameModel
from navigation import NavigationController, Screen
from utils import resize_table_view, load_key, generate_and_store_key
from utils.security import load_encrypted_db_credentials
from view import AbstractView
from view.database_connection_dialog import DatabaseConnectionDialog, get_database_files
from viewmodel import MainViewModel


class MainView(AbstractView):
    # Signal for switching to table view
    data_viewer_table_name = pyqtSignal(str)

    @property
    def view_model(self):
        return self._view_model

    @property
    def nav_controller(self):
        return self._nav_controller

    def __init__(self, view_model: MainViewModel, nav_controller: NavigationController):
        super().__init__()
        self._view_model = view_model
        self._nav_controller = nav_controller
        self._nav_bar = None
        self._nav_main = None
        self._nav_auto_clean = None
        self._nav_analytics = None
        self._nav_button_group = None
        self.tables = None
        self.progress_message_box = None
        self.stats: dict = {}

        # ----------------------------------------------------------------------
        # --- No Database Loaded Layout ---
        # ----------------------------------------------------------------------

        self.no_database_label = QLabel("No Database Loaded")
        self.no_database_label.setFont(QFont(self.font, 24, QFont.Weight.Bold))
        self.no_database_description = QLabel("Use the button in the top right to load a database!")
        self.no_database_description.setFont(QFont(self.font, 14, QFont.Weight.Normal))

        self.no_database_container = QWidget()
        self.no_database_container.setLayout(QVBoxLayout())
        self.no_database_container.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.no_database_container.layout().addWidget(self.no_database_label)
        self.no_database_container.layout().addWidget(self.no_database_description)

        self.no_database_scroll_area = QScrollArea()
        self.no_database_scroll_area.setWidget(self.no_database_container)
        self.no_database_scroll_area.setWidgetResizable(True)

        # ----------------------------------------------------------------------
        # --- Database Layout ---
        # ----------------------------------------------------------------------

        # Set up scroll area for tables with container
        self.table_container = QWidget()
        self.table_container.setLayout(QVBoxLayout())
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidget(self.table_container)
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setMinimumWidth(900)
        table_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        # Database layout
        self.database_label = QLabel("Database Preview")
        self.database_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.database_label.setFont(QFont(self.font, 24))

        # Main screen buttons
        self.load_button = QPushButton("Load Database")
        self.load_button.clicked.connect(self.show_database_connection_dialog)
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.open_export_file_dialog)

        self.database_label_row = QHBoxLayout()
        self.database_label_row.addWidget(self.database_label)
        self.database_label_row.addStretch()

        for button in [self.load_button, self.export_button]:
            button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            button.setFont(QFont(self.font, 14))
            self.database_label_row.addWidget(button)

        # Stats box and scroll area
        self.stats_box = QWidget()
        self.stats_box.setLayout(QVBoxLayout())
        stats_scroll_area = QScrollArea()
        stats_scroll_area.setWidget(self.stats_box)
        stats_scroll_area.setWidgetResizable(True)
        stats_scroll_area.setMinimumWidth(300)

        # Create a splitter for the table view and stats box
        self.splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.splitter.addWidget(table_scroll_area)
        self.splitter.addWidget(stats_scroll_area)
        self.splitter.setSizes([900, 300])
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setHandleWidth(5)

        # Connect splitter changes to table resizing
        self.splitter.splitterMoved.connect(self.redraw_tables)

        # Navigation
        self.setup_navigation()

        # Main layout
        self.database_layout = QVBoxLayout()
        self.database_layout.addWidget(self._nav_bar)
        self.database_layout.addLayout(self.database_label_row)
        self.database_layout.addWidget(self.no_database_scroll_area)
        self.database_layout.addWidget(self.splitter)

        # ----------------------------------------------------------------------
        # --- Initialize UI ---
        # ----------------------------------------------------------------------

        # Initialize UI with the layout
        self.setLayout(self.database_layout)
        self.no_database_scroll_area.setVisible(True)
        self.splitter.setVisible(False)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.data_changed.connect(self.update_tables)
        self._view_model.data_changed.connect(self.populate_stats)
        self._view_model.database_loaded_changed.connect(self.update_display)
        self._view_model.database_loading_progress.connect(self.update_loading_progress)
        self._view_model.database_loading_error.connect(self.show_database_loading_error)
        self._view_model.exporting_changed.connect(self.export_button.setDisabled)
        self._view_model.exporting_completion.connect(self.show_export_completion_message)
        self._view_model.exporting_error.connect(self.show_export_error_message)

        # Connect navigation controller to UI
        self._nav_controller.nav_destination_changed.connect(self.update_nav_bar)

        # Check for existing database credentials
        generate_and_store_key()  # Does nothing if key already exists
        db_credentials = load_encrypted_db_credentials(load_key())
        if db_credentials:
            self._view_model.set_save_credentials(True)
            self._view_model.load_database(**db_credentials)
            self.show_progress_message_box()

    def setup_navigation(self):
        super().setup_navigation()
        self._nav_main.setChecked(True)

    @QtCore.pyqtSlot(dict)
    def update_tables(self, tables: dict[str, DataFrame]):
        self.tables = tables

        # Clear existing tables from layout
        layout = self.table_container.layout()

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Add a QTableView for each DataFrame
        for table_name, df in tables.items():
            # Limit rows for preview
            df_preview = df.head(10)

            # Create a label for the table name
            label = QLabel(f"<b>{table_name}</b>")
            label.setFont(QFont(self.font, 16, QFont.Weight.Bold))
            layout.addWidget(label)

            # Create the table and set model
            table_view = QTableView()
            model = DataFrameModel(df_preview)
            table_view.setModel(model)

            # Add click event, using partial to avoid late binding
            table_view.clicked.connect(partial(self.enter_table_view, table_name))

            # Update table sizing
            resize_table_view(table_view)

            layout.addWidget(table_view)

        # Update the container in the view
        self.table_container.updateGeometry()

    @QtCore.pyqtSlot(bool)
    def update_display(self, loaded: bool):
        """Update the main view and the progress message box."""
        if self.progress_message_box:
            if loaded:
                self.progress_message_box.setText("Database loaded successfully.")
            else:
                self.progress_message_box.setText("Failed to load the database.")
            self.progress_message_box.button(QMessageBox.StandardButton.Ok).setEnabled(True)

        if loaded:
            self.no_database_scroll_area.setVisible(False)
            self.splitter.setVisible(True)
        else:
            self.no_database_scroll_area.setVisible(True)
            self.splitter.setVisible(False)

    @QtCore.pyqtSlot(dict)
    def populate_stats(self, tables: dict[str, DataFrame]):
        layout = self.stats_box.layout()

        # Clear existing stats from layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Calculate stats
        self.stats = {
            "total_tables": len(tables),
            "total_records": [df.shape[0] for df in tables.values()],
            "total_columns": [df.shape[1] for df in tables.values()],
            "memory_space": [round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3) for df in tables.values()],
            "missing_values": [df.isna().sum().sum() for df in tables.values()],
        }

        # Create display stats for view
        display_stats = [
            f"Total Tables: {self.stats['total_tables']}",
            f"Total Records: {sum(self.stats['total_records'])}",
        ]
        for i, table_name in enumerate(tables.keys()):
            display_stats.append(f"  - {table_name}: {self.stats['total_records'][i]}")
        display_stats.append(f"Total Columns: {sum(self.stats['total_columns'])}")
        for i, table_name in enumerate(tables.keys()):
            display_stats.append(f"  - {table_name}: {self.stats['total_columns'][i]}")
        display_stats.append(f"Missing Values: {sum(self.stats['missing_values'])}")
        for i, table_name in enumerate(tables.keys()):
            display_stats.append(f"  - {table_name}: {self.stats['missing_values'][i]}")
        display_stats.append(f"Memory Usage: {sum(self.stats['memory_space'])} MB")
        for i, table_name in enumerate(tables.keys()):
            display_stats.append(f"  - {table_name}: {self.stats['memory_space'][i]} MB")

        # Add label for the stats box
        stats_label = QLabel("Database Statistics")
        stats_label.setFont(QFont(self.font, 18, QFont.Weight.Bold))
        layout.addWidget(stats_label)

        # Add stats to layout
        for stat in display_stats:
            label = QLabel(stat)
            label.setWordWrap(True)
            label.setFont(QFont(self.font, 12, QFont.Weight.Normal))
            layout.addWidget(label)

        layout.addStretch()

        # Update the container in the view
        self.stats_box.updateGeometry()

    def redraw_tables(self):
        # Resize table views
        if self.tables:
            layout = self.table_container.layout()
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QTableView):
                    resize_table_view(widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Resize table views when window is resized
        self.redraw_tables()

    def show_database_connection_dialog(self):
        dialog = DatabaseConnectionDialog()
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            if DatabaseConnectionDialog.using_files:
                # Get file list Signal view model
                file_list = get_database_files()
                csv_config = dialog.get_csv_config()
                self.show_progress_message_box()
                self._view_model.load_files(file_list, csv_config)
            else:
                # Get connection details and signal view model
                connection_details = dialog.get_connection_details()
                self.show_progress_message_box()
                save_credentials = connection_details.pop("save")
                self._view_model.set_save_credentials(save_credentials)
                self._view_model.load_database(**connection_details)

    def show_progress_message_box(self):
        """Show a message box for database loading progress."""
        self.progress_message_box = QMessageBox()
        self.progress_message_box.setIcon(QMessageBox.Icon.NoIcon)
        self.progress_message_box.setWindowTitle("Database Loading")
        self.progress_message_box.setText("Establishing Connection...")
        self.progress_message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.progress_message_box.button(QMessageBox.StandardButton.Ok).setEnabled(False)
        self.progress_message_box.show()

    def update_loading_progress(self, progress: str):
        """Update the progress message box."""
        if self.progress_message_box:
            self.progress_message_box.setText(progress)

    def show_database_loading_error(self, error: str):
        """Handle database loading errors."""
        if self.progress_message_box:
            self.progress_message_box.setIcon(QMessageBox.Icon.Critical)
            self.progress_message_box.setText("Database Loading Error")
            self.progress_message_box.setInformativeText(error)
            self.progress_message_box.button(QMessageBox.StandardButton.Ok).setEnabled(True)

    def enter_table_view(self, table_name: str):
        self.data_viewer_table_name.emit(table_name)
        self._view_model.set_nav_destination(Screen.DATA_TABLE)

    def open_export_file_dialog(self):
        export_dialog = QFileDialog()
        directory = export_dialog.getExistingDirectory(self, "Select Directory", ".", QFileDialog.Option.ShowDirsOnly)

        if directory:
            self._view_model.export_data(directory)

    def show_export_completion_message(self, message: str):
        self.progress_message_box = QMessageBox()
        self.progress_message_box.setWindowTitle("Database Export")
        self.progress_message_box.setText(message)
        self.progress_message_box.show()

    def show_export_error_message(self, error: str):
        self.progress_message_box = QMessageBox()
        self.progress_message_box.setWindowTitle("Database Export")
        self.progress_message_box.setText("There was an error exporting the database.")
        self.progress_message_box.setInformativeText(error)
        self.progress_message_box.setIcon(QMessageBox.Icon.Warning)
        self.progress_message_box.show()
