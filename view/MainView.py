from PyQt6 import QtCore
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTableView, QVBoxLayout, QWidget, QScrollArea, QLabel, QSizePolicy, QHBoxLayout, \
    QHeaderView, QListView
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
        self._nav_bar = None
        self._nav_main = None
        self._nav_auto_clean = None
        self._nav_analytics = None
        self._button_group = None
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

        # Database layout
        database_layout = QHBoxLayout()
        self.database_label = QLabel("Database Preview")
        self.database_label.setFont(QFont("Cascadia Code", 24))

        # TODO: Add stats box and buttons
        stats_box = QListView()
        stats_box.setFixedWidth(400)

        database_layout.addWidget(scroll_area)
        database_layout.addWidget(stats_box)

        # Navigation
        self.setup_navigation()

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self._nav_bar)
        layout.addWidget(self.database_label)
        layout.addLayout(database_layout)
        self.setLayout(layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.data_changed.connect(self.update_tables)
        self._view_model.database_loaded_changed.connect(self.update_display)

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

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Resize table views when window is resized
        if self.tables:
            layout = self.table_container.layout()
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QTableView):
                    resize_table_view(widget)

def resize_table_view(table_view: QTableView):
    # Set size policy and scroll mode
    table_view.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    table_view.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

    default_column_width = 200

    # Set column widths
    header = table_view.horizontalHeader()
    header.setDefaultSectionSize(default_column_width)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

    # Calculate total width needed for all columns
    total_width = default_column_width * table_view.model().columnCount()
    total_width += table_view.frameWidth() * 2
    total_width += table_view.verticalHeader().width()

    table_view.setMaximumWidth(total_width)

    # Fit height to show all rows in preview
    def update_height():
        row_height = table_view.verticalHeader().defaultSectionSize()
        header_height = table_view.horizontalHeader().height()
        frame_height = table_view.frameWidth() * 2
        has_scroll_bar = table_view.horizontalScrollBar().isVisible()
        scroll_bar_height = table_view.horizontalScrollBar().height() if has_scroll_bar else 0

        total_height = header_height + (row_height * table_view.model().rowCount()) + frame_height + scroll_bar_height
        table_view.setFixedHeight(total_height)

    # Defer until event loop has a chance to lay out the table
    QtCore.QTimer.singleShot(0, update_height)
