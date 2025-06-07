import pandas as pd
from pandas import Series, DataFrame
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns
from model import DataModel
from services import AbstractService, ModelEditor
from utils import MplCanvas


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
        self._table_name = None
        self._table: DataFrame = pd.DataFrame()
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

    def set_table(self, table_name: str):
        self._table_name = table_name
        self._table = self._model.get_table(table_name)

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

    def create_missingness_plot(self, canvas: MplCanvas):
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        msno.matrix(self._table, ax=ax, sparkline=False)
        ax.set_title("Missingness Distribution per Column")
        canvas.draw()

    def create_outlier_plot(self, canvas: MplCanvas):
        df_numeric = self._table.select_dtypes(include="number")
        df_dates = self._table.select_dtypes(include=["datetime", "datetime64[ns]"]).copy()
        df_strings = self._table.select_dtypes(include=["object", "string"]).copy()

        # Convert dates to ordinal, avoiding missing values
        for col in df_dates.columns:
            df_dates[col] = df_dates[col].map(
                lambda x: pd.Timestamp(x).toordinal() if pd.notnull(x) else None
            )

        # Convert strings to length
        for col in df_strings.columns:
            df_strings[col] = df_strings[col].astype(str).str.len()

        # Combine all DataFrames
        df_combined = pd.concat([df_numeric, df_dates, df_strings], axis=1)

        # Normalize column values
        def min_max_norm(series):
            min_val = series.min()
            max_val = series.max()
            if min_val == max_val:
                return series * 0  # Constant Series of all 0s
            return (series - min_val) / (max_val - min_val)

        df_normalized = df_combined.apply(min_max_norm)

        df_melted = df_normalized.melt(var_name="column", value_name="value").dropna()

        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        sns.boxplot(x="column", y="value", data=df_melted, showfliers=True, ax=ax)
        ax.set_title("Boxplot for Outliers (Numeric, Dates, and String Lengths [Normalized])")
        ax.tick_params(axis='x', labelrotation=45)
        canvas.draw()

    def create_distribution_plot(self, column: str, canvas: MplCanvas):
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        sns.histplot(self._table[column], kde=True, bins = 30, ax=ax)
        ax.set_title(f"Distribution Plot for {column.title()}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        canvas.draw()

    def generate_suggestions(self):
        # TODO: Implement generate_suggestions
        pass

    def save_stats(self):
        # TODO: Implement save_stats
        pass

    def save_plots(self):
        # TODO: Implement save_plots
        pass
