import pandas as pd
from pandas import DataFrame

from model import DataModel
from services import AbstractService


class AnalyticsService(AbstractService):
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
        return self._plot_data

    @property
    def suggestions(self) -> dict:
        return self._suggestions

    @property
    def analytics_available(self) -> bool:
        return self._analytics_available

    def __init__(self, model: DataModel):
        self._model = model
        self._analytics_config = None
        self._table_name = None
        self._table: DataFrame = pd.DataFrame()
        self._statistics = {}
        self._plot_data = {}
        self._suggestions = {}
        self._analytics_available = False

    def set_table(self, table_name: str):
        self._table_name = table_name
        self._table = self._model.get_table(table_name)

    def reset_analytics(self):
        self._statistics = {}
        self._plot_data = {}
        self._suggestions = {}
        self._analytics_available = False

    def set_analytics_config(self, analytics_config):
        self._analytics_config = analytics_config

    def set_analytics_available(self, analytics_available):
        self._analytics_available = analytics_available

    def get_outlier_columns(self) -> DataFrame:
        """Returns a DataFrame with only the columns of the current table that
        are relevant for outlier calculations. This includes numeric columns,
        datetime columns, and the lengths of string/object columns."""
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

        return df_combined

    def calculate_missingness_stats(self):
        self._statistics["missingness"] = {}

        for column in self._table.columns:
            missing = self._table[column].isna().sum()
            percent_missing = missing / len(self._table) * 100
            self._statistics["missingness"][column] = percent_missing

    def calculate_category_stats(self):
        self._statistics["categories"] = {}

        for column in self._table.columns:
            if self._table[column].dtype == "category":
                category_counts = self._table[column].value_counts()
                self._statistics["categories"][column] = category_counts.to_dict()

    def calculate_outlier_stats(self):
        self._statistics["outliers"] = {}

        df_outliers = self.get_outlier_columns()
        for column in df_outliers.columns:
            q1 = df_outliers[column].quantile(0.25)
            q3 = df_outliers[column].quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            lower_outlier_count = df_outliers[df_outliers[column] < lower_bound].shape[0]
            upper_outlier_count = df_outliers[df_outliers[column] > upper_bound].shape[0]

            self._statistics["outliers"][column] = {
                "lower": lower_outlier_count,
                "upper": upper_outlier_count,
            }

    def create_missingness_plot_data(self):
        self._plot_data["missingness"] = self._table

    def create_outlier_plot_data(self):
        df_combined = self.get_outlier_columns()

        # Normalize column values
        def min_max_norm(series):
            min_val = series.min()
            max_val = series.max()
            if min_val == max_val:
                return series * 0  # Constant Series of all 0s
            return (series - min_val) / (max_val - min_val)

        df_normalized = df_combined.apply(min_max_norm)
        self._plot_data["outliers"] = df_normalized

    def create_distribution_plot_data(self, column: str):
        # Drop missing values for plotting
        series = self._table[column].dropna()

        # Skip empty or non-numeric columns
        if series.empty or not (pd.api.types.is_numeric_dtype(series) or pd.api.types.is_datetime64_any_dtype(series)):
            return

        self._plot_data.setdefault("distributions", {})
        self._plot_data["distributions"][column] = series

    def generate_suggestions(self):
        self._suggestions["missingness"] = (
            "If a column contains only 5% or fewer missing values, "
            "the records with missing values can be dropped. If there are more than 5% missing values, "
            "consider imputing values with measures of center. Imputing with the mean is appropriate for "
            "columns with a roughly normal distribution, whereas imputing with the median is appropriate for "
            "columns with a skewed distribution. For non-numeric columns, consider imputing with the mode."
        )

        self._suggestions["outliers"] = (
            "Outliers can impact the distribution of a column by "
            "\"pulling\" the mean in one direction or the other. They can also make it more difficult "
            "for machine learning models to learn patterns in the dataset. For numeric columns, consider "
            "dropping records containing outliers. For datetime columns or string columns, use the query "
            "tool in the table view screen to examine outlying dates or long/short strings more closely "
            "for issues."
        )


        self._suggestions["categories"] = (
            "This tool can catch minor spelling errors in category names, but larger errors or extraneous "
            "categories may go unprocessed. Examine the category list below for each categorical column. "
            "If necessary, provide a correction map for cleaning the remaining categories. Format the map as "
            "follows: \"[incorrect_category]: [corrected_category]\". Use commas to separate entries."
        )

        self._suggestions["distributions"] = (
            "Machine learning models can struggle with numeric data that follows a skewed distribution. "
            "Consider standardizing columns that do not follow a normal distribution or have many outliers."
        )

    def save_stats(self):
        # TODO: Implement save_stats
        pass

    def save_plots(self):
        # TODO: Implement save_plots
        pass
