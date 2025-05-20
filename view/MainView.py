from PyQt6 import QtCore
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTableView, QVBoxLayout, QWidget, QScrollArea, QLabel, QSizePolicy, QHeaderView, QSplitter
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
        self.font = "Cascadia Code"

        # Set up scroll area for tables with container
        self.table_container = QWidget()
        self.table_container.setLayout(QVBoxLayout())
        table_scroll_area = QScrollArea()
        table_scroll_area.setWidget(self.table_container)
        table_scroll_area.setWidgetResizable(True)
        table_scroll_area.setMinimumWidth(500)
        table_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        # Database layout
        self.database_label = QLabel("Database Preview")
        self.database_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.database_label.setFont(QFont(self.font, 24))

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
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

        # Navigation
        self.setup_navigation()

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self._nav_bar)
        layout.addWidget(self.database_label)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.data_changed.connect(self.update_tables)
        self._view_model.data_changed.connect(self.populate_stats)
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
            label.setFont(QFont(self.font, 16, QFont.Weight.Bold))
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

    @QtCore.pyqtSlot(bool)
    def update_display(self, loaded: bool):
        # TODO: Implement update_display
        pass

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

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Resize table views when window is resized
        if self.tables:
            layout = self.table_container.layout()
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QTableView):
                    resize_table_view(widget)

    def on_splitter_moved(self, pos, index):
        # Resize table views when splitter is moved
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
