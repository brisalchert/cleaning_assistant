import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

from services import DataCleaningService, AnalyticsService
from utils import Configuration, MplCanvas


class CleaningWorker(QObject):
    finished: pyqtSignal = pyqtSignal(bool)
    error: pyqtSignal = pyqtSignal(str)
    progress: pyqtSignal = pyqtSignal(int)
    step: pyqtSignal = pyqtSignal(str)
    cleaning_operations: pyqtSignal = pyqtSignal(int)
    data_types_converted: pyqtSignal = pyqtSignal(int)
    duplicates_removed: pyqtSignal = pyqtSignal(int)
    outliers_removed: pyqtSignal = pyqtSignal(int)
    missing_values_dropped: pyqtSignal = pyqtSignal(int)
    missing_values_imputed: pyqtSignal = pyqtSignal(int)

    def __init__(self, data_cleaning_service: DataCleaningService, analytics_service: AnalyticsService, cleaning_config: dict, analytics_config: dict):
        super().__init__()
        self.data_cleaning_service = data_cleaning_service
        self.analytics_service = analytics_service
        self.cleaning_config = cleaning_config
        self.analytics_config = analytics_config

    def run(self):
        """Apply the cleaning and analytics scripts using a separate thread."""
        try:
            self.step.emit("Starting cleaning script...")

            # Column-specific cleaning
            for column, options in self.cleaning_config[Configuration.COLUMNS].items():
                for key, value in options.items():
                    if key == Configuration.DATA_TYPE:
                        self.step.emit("Changing data types...")
                        types_changed = self.data_cleaning_service.set_data_type(column, value)
                        self.data_types_converted.emit(types_changed)
                        self.cleaning_operations.emit(self.data_cleaning_service.get_table_length() * types_changed)
                        self.progress.emit(10)
                    elif key == Configuration.INT_MIN:
                        self.step.emit("Removing integer outliers...")
                        min_int = int(value) if value != "" else float("-inf")
                        dropped = self.data_cleaning_service.drop_outliers(column, min_int, float("inf"))
                        self.outliers_removed.emit(dropped)
                        self.cleaning_operations.emit(dropped)
                    elif key == Configuration.INT_MAX:
                        self.step.emit("Removing integer outliers...")
                        max_int = int(value) if value != "" else float("inf")
                        dropped = self.data_cleaning_service.drop_outliers(column, float("-inf"), max_int)
                        self.outliers_removed.emit(dropped)
                        self.cleaning_operations.emit(dropped)
                        self.progress.emit(20)
                    elif key == Configuration.FLOAT_MIN:
                        self.step.emit("Removing floating point outliers...")
                        min_float = float(value) if value != "" else float("-inf")
                        dropped = self.data_cleaning_service.drop_outliers(column, min_float, float("inf"))
                        self.outliers_removed.emit(dropped)
                        self.cleaning_operations.emit(dropped)
                    elif key == Configuration.FLOAT_MAX:
                        self.step.emit("Removing floating point outliers...")
                        max_float = float(value) if value != "" else float("inf")
                        dropped = self.data_cleaning_service.drop_outliers(column, float("-inf"), max_float)
                        self.outliers_removed.emit(dropped)
                        self.cleaning_operations.emit(dropped)
                        self.progress.emit(20)
                    elif key == Configuration.STRING_MAX:
                        self.step.emit("Trimming strings...")
                        max_length = int(value) if value != "" else 1000000
                        changed = self.data_cleaning_service.truncate_strings(column, max_length)
                        self.cleaning_operations.emit(changed)
                        self.progress.emit(30)
                    elif key == Configuration.DATE_MIN:
                        self.step.emit("Removing date outliers...")
                        dropped = self.data_cleaning_service.drop_date_outliers(column, pd.to_datetime(value), pd.to_datetime("2100-01-01"))
                        self.outliers_removed.emit(dropped)
                        self.cleaning_operations.emit(dropped)
                    elif key == Configuration.DATE_MAX:
                        self.step.emit("Removing date outliers...")
                        dropped = self.data_cleaning_service.drop_date_outliers(column, pd.to_datetime("1900-01-01"), pd.to_datetime(value))
                        self.outliers_removed.emit(dropped)
                        self.cleaning_operations.emit(dropped)
                        self.progress.emit(30)
                    elif key == Configuration.CATEGORIES:
                        self.step.emit("Correcting categories...")
                        if value != "":
                            changed = self.data_cleaning_service.autocorrect_categories(column, value.split()) # TODO: Make note of splitting on whitespace
                            self.cleaning_operations.emit(changed)

            self.progress.emit(40)

            # General cleaning
            if self.cleaning_config[Configuration.DELETE_DUPLICATES]:
                self.step.emit("Deleting duplicate records...")
                dropped = self.data_cleaning_service.drop_duplicates()
                self.duplicates_removed.emit(dropped)
                self.cleaning_operations.emit(dropped)

            self.progress.emit(60)

            if self.cleaning_config[Configuration.DROP_MISSING]:
                self.step.emit("Dropping records with missing values...")
                dropped = self.data_cleaning_service.drop_missing_all()
                self.missing_values_dropped.emit(dropped)
                self.cleaning_operations.emit(dropped)
            elif self.cleaning_config[Configuration.IMPUTE_MISSING_MEAN]:
                self.step.emit("Imputing missing values with mean...")
                imputed = self.data_cleaning_service.impute_missing_mean_all()
                self.missing_values_imputed.emit(imputed)
                self.cleaning_operations.emit(imputed)
            elif self.cleaning_config[Configuration.IMPUTE_MISSING_MEDIAN]:
                self.step.emit("Imputing missing values with median...")
                imputed = self.data_cleaning_service.impute_missing_median_all()
                self.missing_values_imputed.emit(imputed)
                self.cleaning_operations.emit(imputed)

            self.progress.emit(75)
            self.step.emit("Generating cleaning script...")
            self.data_cleaning_service.generate_cleaning_script(self.cleaning_config)

            self.progress.emit(80)
            self.step.emit("Gathering analytics...")
            # TODO: Add analytics gathering
            self.analytics_service.create_missingness_plot(MplCanvas())
            self.progress.emit(85)
            self.analytics_service.create_outlier_plot(MplCanvas())
            self.progress.emit(95)
            self.analytics_service.create_distribution_plot("release_date", MplCanvas())

            self.progress.emit(100)
            self.finished.emit(True)

        except Exception as e:
            self.error.emit(f"Error cleaning data: {str(e)}")
            self.finished.emit(False)
