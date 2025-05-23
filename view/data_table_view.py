import pandas as pd
from PyQt6 import QtCore
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QSizePolicy, QLabel, QComboBox, QHBoxLayout, QTableView, QScrollArea
from pandas import DataFrame
from model import DataFrameModel
from navigation import NavigationController
from utils import resize_table_view
from view import AbstractView
from viewmodel import DataViewerViewModel


class DataTableView(AbstractView):
    @property
    def view_model(self):
        return self._view_model

    @property
    def nav_controller(self):
        return self._nav_controller

    def __init__(self, view_model: DataViewerViewModel, nav_controller: NavigationController):
        super().__init__()
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
        self.page: int = 1
        self.page_size: int = 50
        self.editing: bool = False
        self.query_result: DataFrame = pd.DataFrame()

        # Set up scroll area for tables with container
        self.table_container = QWidget()
        self.table_container.setLayout(QVBoxLayout())
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidget(self.table_container)
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setMinimumWidth(500)
        table_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Database layout
        self.table_name_label = QLabel(self.table_name)
        self.table_name_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.table_name_label.setFont(QFont(self.font, 24))

        # Data table screen buttons and menus
        self.sort_dropdown = QComboBox()
        self.filter_dropdown = QComboBox()

        self.button_row = QHBoxLayout()
        self.button_row.addWidget(self.table_name_label)
        self.button_row.addStretch()

        for widget in [self.sort_dropdown, self.filter_dropdown]:
            widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            widget.setFont(QFont(self.font, 14))
            self.button_row.addWidget(widget)

        # Navigation
        self.setup_navigation()

        # Main Layout
        self.data_table_layout = QVBoxLayout()
        self.data_table_layout.addWidget(self._nav_bar)
        self.data_table_layout.addLayout(self.button_row)
        self.data_table_layout.addWidget(table_scroll_area)

        # ----------------------------------------------------------------------
        # --- Initialize UI ---
        # ----------------------------------------------------------------------

        # Initialize UI with the layout
        self.setLayout(self.data_table_layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.data_changed.connect(self.update_table)
        self._view_model.is_editing_changed.connect(self.update_editing)
        self._view_model.query_result_changed.connect(self.update_query_result)

    @QtCore.pyqtSlot(dict)
    def update_table(self, table: dict):
        self.table_name = table["table_name"]
        self.table = table["data"]

        # Clear existing table from layout
        layout = self.table_container.layout()
        if layout.count():
            widget = layout.takeAt(0).widget()
            if widget:
                widget.setParent(None)

        # Add the QTableView for the DataFrame
        self.table_view = QTableView()
        self.table_page = self.get_page_dataframe()
        model = DataFrameModel(self.table_page)
        self.table_view.setModel(model)

        # Update table sizing
        resize_table_view(self.table_view)

        layout.addWidget(self.table_view)

        # Update the container in the view
        self.table_container.updateGeometry()

    def get_page_dataframe(self):
        start_index = (self.page - 1) * self.page_size
        end_index = min(self.page * self.page_size, len(self.table))
        return self.table.iloc[start_index:end_index]

    def update_page(self, page: int):
        if page != self.page:
            self.page = page
            self.update_table(self.table)

    def update_page_size(self, page_size: int):
        self.page_size = page_size

        # Reset to first page
        self.update_page(1)

    def update_editing(self, editing: bool):
        self.editing = editing

    def update_query_result(self, query_result: DataFrame):
        self.query_result = query_result

    def sort_results(self, by: str, ascending: bool):
        # Sort the table and update the view
        self.table.sort_values(by, ascending=ascending, inplace=True)
        self.update_table(self.table)

    def filter_results(self, by: str, value: str):
        # TODO: Implement filter_results
        pass
