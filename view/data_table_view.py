import pandas as pd
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QModelIndex, QSize, QTimer, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QLabel, QComboBox, QHBoxLayout, QTableView, QScrollArea, \
    QSplitter, QTextEdit, QPushButton, QLineEdit, QDialog, QMessageBox
from pandas import DataFrame

from model import DataFrameModel
from navigation import NavigationController
from utils import resize_table_view
from utils.transformations import load_flipped_inverted_icon
from view import AbstractView
from viewmodel import DataViewerViewModel


def update_button_enabled(button: QPushButton, enabled: bool):
    button.clearFocus()
    button.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False)
    button.update()
    QTimer.singleShot(0, lambda: button.setEnabled(enabled))

class DataTableView(AbstractView):
    @property
    def view_model(self):
        return self._view_model

    @property
    def nav_controller(self):
        return self._nav_controller

    def __init__(self, view_model: DataViewerViewModel, nav_controller: NavigationController):
        super().__init__()
        self.stats = None
        self._view_model = view_model
        self._nav_controller = nav_controller
        self._nav_bar = None
        self._nav_main = None
        self._nav_auto_clean = None
        self._nav_analytics = None
        self._nav_button_group = None
        self.table_name = None
        self.table: DataFrame = pd.DataFrame()
        self.table_page: DataFrame = pd.DataFrame()
        self.table_view = None
        self.table_model = None
        self.table_filtered: DataFrame = pd.DataFrame()
        self.filtered = False

        self.page: int = 1
        self.page_size: int = 50
        self.editing: bool = False
        self.query_result: DataFrame = pd.DataFrame()

        # Set up scroll area for table view with container
        self.table_container = QWidget()
        self.table_container.setLayout(QVBoxLayout())
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidget(self.table_container)
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setMinimumWidth(900)
        table_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Data table label
        self.table_name_label = QLabel(self.table_name)
        self.table_name_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.table_name_label.setFont(QFont(self.font, 24))

        # Data table screen buttons and menus
        self.button_row = QHBoxLayout()
        self.button_row.addWidget(self.table_name_label)

        self.prev_page_button = QPushButton()
        icon = load_flipped_inverted_icon("assets/arrow.png", flip_horizontal=True, invert=True)
        self.prev_page_button.setIcon(icon)
        self.prev_page_button.setIconSize(QSize(24, 24))
        self.prev_page_button.clicked.connect(self.on_prev_page_button_clicked)

        self.page_number = QLineEdit("1")
        self.page_number.setFixedWidth(100)
        self.page_number.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.page_number.returnPressed.connect(lambda: self.update_page(int(self.page_number.text())))
        self.page_limit = QLabel("/1")

        self.next_page_button = QPushButton()
        icon = load_flipped_inverted_icon("assets/arrow.png", invert=True)
        self.next_page_button.setIcon(icon)
        self.next_page_button.setIconSize(QSize(24, 24))
        self.next_page_button.clicked.connect(self.on_next_page_button_clicked)

        self.edit_toggle_button = QPushButton("Enter Edit Mode")
        self.edit_toggle_button.setCheckable(True)
        self.edit_toggle_button.clicked.connect(lambda: self._view_model.toggle_editing())

        self.undo_button = QPushButton("Undo")
        self.undo_button.setEnabled(False)
        self.undo_button.clicked.connect(self._view_model.undo_change)
        self.redo_button = QPushButton("Redo")
        self.redo_button.setEnabled(False)
        self.redo_button.clicked.connect(self._view_model.redo_change)

        for widget in [
            self.prev_page_button,
            self.page_number,
            self.page_limit,
            self.next_page_button,
            self.edit_toggle_button,
            self.undo_button,
            self.redo_button
        ]:
            widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            widget.setFont(QFont(self.font, 14))
            self.button_row.addWidget(widget)

        self.button_row.addStretch()

        self.sort_box = QVBoxLayout()
        self.sort_label = QLabel("Sort by:")
        self.sort_dropdown = QComboBox()
        self.sort_dropdown.currentIndexChanged.connect(lambda: self.sort_results(*self.get_sort()))
        self.sort_box.addWidget(self.sort_label)
        self.sort_box.addWidget(self.sort_dropdown)

        self.filter_box = QVBoxLayout()
        self.filter_label = QLabel("Filter by:")
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.currentIndexChanged.connect(lambda: self.filter_results(*self.get_filter()))
        self.filter_box.addWidget(self.filter_label)
        self.filter_box.addWidget(self.filter_dropdown)

        for widget in [self.sort_label, self.sort_dropdown, self.filter_label, self.filter_dropdown]:
            widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            widget.setFont(QFont(self.font, 10))

        self.button_row.addLayout(self.sort_box)
        self.button_row.addLayout(self.filter_box)

        # Set up stats and query section
        self.stats_box = QWidget()
        self.stats_box.setLayout(QVBoxLayout())
        self.stats_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        stats_scroll_area = QScrollArea()
        stats_scroll_area.setWidget(self.stats_box)
        stats_scroll_area.setWidgetResizable(True)
        stats_scroll_area.setMinimumWidth(300)

        self.query_window = QWidget()
        self.query_window.setLayout(QVBoxLayout())
        self.query_window.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.query_text_edit = QTextEdit()
        self.execute_button = QPushButton("Execute Query")
        self.execute_button.clicked.connect(lambda: self._view_model.execute_query(self.query_text_edit.toPlainText()))
        self.query_window.layout().addWidget(self.query_text_edit)
        self.query_window.layout().addWidget(self.execute_button)

        right_panel = QSplitter(QtCore.Qt.Orientation.Vertical)
        right_panel.addWidget(self.query_window)
        right_panel.addWidget(stats_scroll_area)

        # Create a splitter for the table view and stats box
        self.horizontal_splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.horizontal_splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.horizontal_splitter.addWidget(table_scroll_area)
        self.horizontal_splitter.addWidget(right_panel)
        self.horizontal_splitter.setSizes([900, 300])
        self.horizontal_splitter.setCollapsible(0, False)
        self.horizontal_splitter.setCollapsible(1, False)
        self.horizontal_splitter.setHandleWidth(5)

        # Connect splitter changes to table resizing
        self.horizontal_splitter.splitterMoved.connect(self.redraw_table)

        # Navigation
        self.setup_navigation()

        # Main Layout
        self.data_table_layout = QVBoxLayout()
        self.data_table_layout.addWidget(self._nav_bar)
        self.data_table_layout.addLayout(self.button_row)
        self.data_table_layout.addWidget(self.horizontal_splitter)

        # ----------------------------------------------------------------------
        # --- Initialize UI ---
        # ----------------------------------------------------------------------

        # Initialize UI with the layout
        self.setLayout(self.data_table_layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.data_changed.connect(self.update_table)
        self._view_model.data_changed.connect(self.populate_stats)
        self._view_model.is_editing_changed.connect(self.update_editing)
        self._view_model.query_result_changed.connect(self.update_query_result)
        self._view_model.query_error_changed.connect(self.show_query_error_message)
        self._view_model.undo_available_changed.connect(lambda enabled: update_button_enabled(self.undo_button, enabled))
        self._view_model.redo_available_changed.connect(lambda enabled: update_button_enabled(self.redo_button, enabled))

        # Connect navigation controller to UI
        self._nav_controller.nav_destination_changed.connect(self.update_nav_bar)

    @QtCore.pyqtSlot(dict)
    def update_table(self, table: dict):
        self.table_name = table["table_name"]
        self.table = table["data"]

        # Clear existing table from layout
        layout = self.table_container.layout()
        if layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Add the QTableView for the DataFrame
        self.table_view = QTableView()
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.update_page_size(self.page_size)
        self.update_table_page()

        # Populate sorting/filtering dropdowns
        self.sort_dropdown.clear()
        self.sort_dropdown.addItem("None")
        self.filter_dropdown.clear()
        self.filter_dropdown.addItem("None")

        for column in self.table.columns:
            self.sort_dropdown.addItem(f"{column} (ascending)")
            self.sort_dropdown.addItem(f"{column} (descending)")

            if self.table[column].dtype == "bool":
                self.filter_dropdown.addItem(f"{column} (True)")
                self.filter_dropdown.addItem(f"{column} (False)")

            if self.table[column].dtype == "category":
                for category in self.table[column].cat.categories:
                    self.filter_dropdown.addItem(f"{column} ({category})")

        # Update table sizing
        resize_table_view(self.table_view)

        layout.addWidget(self.table_view)

        # Update the container in the view
        self.table_container.updateGeometry()
        self.table_name_label.setText(self.table_name)

    @QtCore.pyqtSlot(dict)
    def populate_stats(self, table: dict):
        layout = self.stats_box.layout()
        df = table["data"]

        # Clear existing stats from layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Calculate stats
        self.stats = {
            "total_records": df.shape[0],
            "total_columns": df.shape[1],
            "memory_space": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3),
            "missing_values": df.isna().sum().sum()
        }

        # Create display stats for view
        display_stats = [
            f"Total Records: {self.stats['total_records']}",
            f"Total Columns: {self.stats['total_columns']}",
            f"Memory Usage: {self.stats['memory_space']} MB",
            f"Missing Values: {self.stats['missing_values']}"
        ]

        # Add label for the stats box
        stats_label = QLabel("Table Statistics")
        stats_label.setFont(QFont(self.font, 16, QFont.Weight.Bold))
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

    def redraw_table(self):
        # Resize table views
        layout = self.table_container.layout()
        if layout.count():
            widget = layout.itemAt(0).widget()
            if isinstance(widget, QTableView):
                resize_table_view(widget)

    def get_page_dataframe(self):
        # Check for filtering
        df = self.table_filtered if self.filtered else self.table

        start_index = (self.page - 1) * self.page_size
        end_index = min(self.page * self.page_size, len(df))
        return df.iloc[start_index:end_index]

    def update_table_page(self):
        self.table_page = self.get_page_dataframe()
        self.table_model = DataFrameModel(self.table_page)
        self.table_model.update_editing(self.editing)
        self.table_model.dataChanged.connect(self.handle_data_changed)
        self.table_view.setModel(None) # Detach old model
        self.table_view.setModel(self.table_model)

    def update_page(self, page: int):
        self.page = page
        self.page_number.setText(str(self.page))
        self.update_table_page()
        self.redraw_table()

    def on_prev_page_button_clicked(self):
        if self.page > 1:
            self.update_page(self.page - 1)

    def on_next_page_button_clicked(self):
        if self.page * self.page_size < len(self.table):
            self.update_page(self.page + 1)

    def update_page_size(self, page_size: int):
        self.page_size = page_size
        self.page_number.setValidator(QtGui.QIntValidator(1, len(self.table) // self.page_size + 1))
        self.page_limit.setText(f"/{len(self.table) // self.page_size + 1}")

        # Reset page
        self.update_page(self.page)

    def update_editing(self, editing: bool):
        self.editing = editing

        if editing:
            self.table_view.model().update_editing(True)
            self.edit_toggle_button.setText("Exit Edit Mode")
            self.edit_toggle_button.setChecked(True)
        else:
            self.table_view.model().update_editing(False)
            self.edit_toggle_button.setText("Enter Edit Mode")
            self.edit_toggle_button.setChecked(False)

    def update_query_result(self, query_result: DataFrame):
        self.query_result = query_result
        self.show_query_result_dialog()

    def show_query_result_dialog(self):
        result_dialog = QDialog()
        result_dialog.setWindowTitle("Query Result")
        result_dialog.setLayout(QVBoxLayout())
        result_dialog.setFixedSize(1000, 600)
        result_dialog_table_view = QTableView()
        result_dialog_model = DataFrameModel(self.query_result)
        result_dialog_table_view.setModel(result_dialog_model)
        result_dialog.layout().addWidget(result_dialog_table_view)
        result_dialog.exec()

    def show_query_error_message(self, error: str):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Query Error")
        error_dialog.setText("There was an error executing your query.")
        error_dialog.setInformativeText(error)
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.exec()

    def show_sorting_error_message(self, error: str):
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Sort Error")
        error_dialog.setText("There was an error performing the action.")
        error_dialog.setInformativeText(error)
        error_dialog.setInformativeText(error)
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.exec()

    def handle_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
        row = top_left.row()
        new_row_df = self.table_view.model().get_dataframe().iloc[[row]]

        # Adjust row for page number
        row_adjusted = row + (self.page - 1) * self.page_size

        self._view_model.update_row(row_adjusted, new_row_df)

    def sort_results(self, by: str, ascending: bool):
        df = self.table_filtered if self.filtered else self.table

        if by is None or ascending is None:
            df.sort_index(ascending=True, inplace=True)
            self.update_page(1)
            return

        # Sort the table and update the view
        try:
            df.sort_values(by, ascending=ascending, inplace=True)
            self.update_page(1)
        except TypeError as e:
            self.show_sorting_error_message(str(e))

    def get_sort(self):
        sort = self.sort_dropdown.currentText()
        if sort == "None" or sort == "":
            return None, None
        else:
            sort = sort.split(" ")
            sort_by = sort[0]
            sort_ascending = sort[1] == "(ascending)"
            return sort_by, sort_ascending

    def filter_results(self, by: str, value: str):
        if by is None or value is None:
            self.filtered = False
            self.update_page(1)
            return

        # Parse boolean values
        if value == "True":
            value = True
        elif value == "False":
            value = False

        # Filter the table and update the view
        self.table_filtered = self.table[self.table[by] == value]
        self.filtered = True
        self.update_page(1)

    def get_filter(self):
        filter_text = self.filter_dropdown.currentText()
        if filter_text == "None" or filter_text == "":
            return None, None
        else:
            filter_text = filter_text.split(" ")
            filter_by = filter_text[0]
            filter_value = filter_text[1].strip("()")
            return filter_by, filter_value
