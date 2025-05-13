import pandas as pd
from PyQt6.QtWidgets import QWidget
from pandas import DataFrame
from navigation import NavigationController
from view.AbstractView import AbstractView
from viewmodel import DataViewerViewModel


class DataTableView(QWidget, AbstractView):
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
        self.table: DataFrame = pd.DataFrame()
        self.page: int = 0
        self.page_size: int = 20
        self.editing: bool = False
        self.query_result: DataFrame = pd.DataFrame()

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.data_changed.connect(self.update_table)
        self._view_model.is_editing_changed.connect(self.update_editing)
        self._view_model.query_result_changed.connect(self.update_query_result)

    def update_table(self, table: DataFrame):
        self.table = table

    def update_page(self, page: int):
        self.page = page

    def update_page_size(self, page_size: int):
        self.page_size = page_size

    def update_editing(self, editing: bool):
        self.editing = editing

    def update_query_result(self, query_result: DataFrame):
        self.query_result = query_result

    def sort_results(self, by: str, ascending: bool):
        # TODO: Implement sort_results
        pass

    def filter_results(self, by: str, value: str):
        # TODO: Implement filter_results
        pass
