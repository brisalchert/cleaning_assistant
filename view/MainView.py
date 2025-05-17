from PyQt6 import QtCore
from PyQt6.QtWidgets import QTableView, QVBoxLayout
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
        self.tables: dict[str, DataFrame] = {}
        self._dataframe_model = None
        self.stats: dict = {}

        self.table = QTableView()

        layout = QVBoxLayout()
        layout.addWidget(self.table)
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
        if tables:
            df = list(tables.values())[0].head(100)
            if self._dataframe_model is None:
                self._dataframe_model = DataFrameModel(df)
                self.table.setModel(self._dataframe_model)
            else:
                self._dataframe_model.set_dataframe(df)

    def update_display(self, loaded: bool):
        # TODO: Implement update_display
        pass
