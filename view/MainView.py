from pandas import DataFrame
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
        self.stats: dict = {}

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.data_changed.connect(self.update_tables)
        self._view_model.database_loaded_changed.connect(self.update_display)

    def update_tables(self, tables: dict[str, DataFrame]):
        # TODO: Implement update_tables
        pass

    def update_display(self, loaded: bool):
        # TODO: Implement update_display
        pass
