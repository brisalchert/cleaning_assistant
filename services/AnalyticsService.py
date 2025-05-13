from pandas import Series

from model import DataModel
from services import AbstractService, ModelEditor


class AnalyticsService(AbstractService, ModelEditor):
    @property
    def model(self) -> DataModel:
        return self._model

    @property
    def analytics_config(self) -> dict:
        return self._analytics_config

    @property
    def statistics(self) -> dict:
        return self._statistics

    @property
    def plots(self) -> dict:
        return self._plots

    @property
    def suggestions(self) -> dict:
        return self._suggestions

    def __init__(self, model: DataModel):
        self._model = model
        self._analytics_config = None
        self._statistics = None
        self._plots = None
        self._suggestions = None

    # --- ModelEditor overrides ---

    def create_row(self, table_name: str, columns: dict) -> bool:
        return self._model.create_row(table_name, columns)

    def read_row(self, table_name: str, primary_key: str) -> Series:
        return self._model.read_row(table_name, primary_key)

    def update_row(self, table_name: str, primary_key: str, columns: dict) -> bool:
        return self._model.update_row(table_name, primary_key, columns)

    def delete_row(self, table_name: str, primary_key: str) -> Series:
        return self._model.delete_row(table_name, primary_key)

    # --- Subclass methods ---

    def set_analytics_config(self, analytics_config):
        self._analytics_config = analytics_config

    def calculate_missingness_stats(self):
        # TODO: Implement calculate_missingness_stats
        pass

    def calculate_category_stats(self):
        # TODO: Implement calculate_category_stats
        pass

    def calculate_outlier_stats(self):
        # TODO: Implement calculate_outlier_stats
        pass

    def create_missingness_plot(self):
        # TODO: Implement create_missingness_plot
        pass

    def create_outlier_plot(self):
        # TODO: Implement create_outlier_plot
        pass

    def create_distribution_plot(self, column: str):
        # TODO: Implement create_distribution_plot
        pass

    def generate_suggestions(self):
        # TODO: Implement generate_suggestions
        pass

    def save_stats(self):
        # TODO: Implement save_stats
        pass

    def save_plots(self):
        # TODO: Implement save_plots
        pass
