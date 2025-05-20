from PyQt6 import QtCore
from PyQt6.QtWidgets import QTableView, QVBoxLayout, QWidget, QScrollArea, QLabel, QSizePolicy, QHeaderView, QHBoxLayout
from pandas import DataFrame
from model.DataFrameModel import DataFrameModel
from navigation import NavigationController
from view import AbstractView
from viewmodel import MainViewModel


class MainView(AbstractView):
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
        self.tables = None
        self.stats: dict = {}

        # Set up scroll area for tables with container
        self.table_container = QWidget()
        self.table_container.setLayout(QVBoxLayout())
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.table_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        # Main layout
        layout = QHBoxLayout()
        layout.addWidget(scroll_area)
        # TODO: Add stats box
        box = QTableView()
        box.setFixedWidth(400)
        layout.addWidget(box)
        self.setLayout(layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.data_changed.connect(self.update_tables)
        self._view_model.database_loaded_changed.connect(self.update_display)

    @QtCore.pyqtSlot(dict)
    def update_tables(self, tables: dict[str, DataFrame]):
        # TODO: Add exception Handling
        # TODO: Add other tables
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
            layout.addWidget(label)

            # Create the table and set model
            table_view = QTableView()
            model = DataFrameModel(df_preview)
            table_view.setModel(model)

            # Update table sizing
            resize_table_view(table_view)

            layout.addWidget(table_view)

        # Update the container in the view
        self.table_container.updateGeometry()

    def update_display(self, loaded: bool):
        # TODO: Implement update_display
        pass

def resize_table_view(table_view: QTableView):
    # Set size and scroll bar policies
    table_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    table_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
    table_view.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

    # Set column widths
    header = table_view.horizontalHeader()
    header.setDefaultSectionSize(200)

    # Fit height to show all rows in preview
    def update_height():
        row_height = table_view.verticalHeader().defaultSectionSize()
        header_height = table_view.horizontalHeader().height()
        frame_height = table_view.frameWidth() * 2
        scroll_bar_height = table_view.horizontalScrollBar().height()

        total_height = header_height + (row_height * table_view.model().rowCount()) + frame_height + scroll_bar_height
        table_view.setFixedHeight(total_height)

    # Defer until event loop has a chance to lay out the table
    QtCore.QTimer.singleShot(0, update_height)
