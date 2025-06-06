import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

from services import DataCleaningService
from utils import Configuration


class CleaningWorker(QObject):
    finished: pyqtSignal = pyqtSignal(bool)
    error: pyqtSignal = pyqtSignal(str)
    progress: pyqtSignal = pyqtSignal(int)
    step: pyqtSignal = pyqtSignal(str)

    def __init__(self, data_cleaning_service: DataCleaningService, cleaning_config: dict, analytics_config: dict):
        super().__init__()
        self.data_cleaning_service = data_cleaning_service
        self.cleaning_config = cleaning_config
        self.analytics_config = analytics_config

    def run(self):
        """Apply the cleaning and analytics scripts using a separate thread."""
        try:
            self.step.emit("Gathering analytics...")
            # TODO: Add analytics gathering
            # TODO: Fix unrecognized missing values (such as "None" or "0")

            self.progress.emit(40)

            self.step.emit("Starting cleaning script...")

            # Column-specific cleaning
            for column, options in self.cleaning_config[Configuration.COLUMNS].items():
                for key, value in options.items():
                    if key == Configuration.DATA_TYPE:
                        self.step.emit("Changing data types...")
                        self.data_cleaning_service.set_data_type(column, value)
                        self.progress.emit(50)
                    elif key == Configuration.INT_MIN:
                        self.step.emit("Removing integer outliers...")
                        min_int = int(value) if value != "" else float("-inf")
                        self.data_cleaning_service.drop_outliers(column, min_int, float("inf"))
                    elif key == Configuration.INT_MAX:
                        self.step.emit("Removing integer outliers...")
                        max_int = int(value) if value != "" else float("inf")
                        self.data_cleaning_service.drop_outliers(column, float("-inf"), max_int)
                        self.progress.emit(60)
                    elif key == Configuration.FLOAT_MIN:
                        self.step.emit("Removing floating point outliers...")
                        min_float = float(value) if value != "" else float("-inf")
                        self.data_cleaning_service.drop_outliers(column, min_float, float("inf"))
                    elif key == Configuration.FLOAT_MAX:
                        self.step.emit("Removing floating point outliers...")
                        max_float = float(value) if value != "" else float("inf")
                        self.data_cleaning_service.drop_outliers(column, float("-inf"), max_float)
                        self.progress.emit(60)
                    elif key == Configuration.STRING_MAX:
                        self.step.emit("Trimming strings...")
                        max_length = int(value) if value != "" else 1000000
                        self.data_cleaning_service.truncate_strings(column, max_length)
                        self.progress.emit(70)
                    elif key == Configuration.DATE_MIN:
                        self.step.emit("Removing date outliers...")
                        self.data_cleaning_service.drop_date_outliers(column, pd.to_datetime(value), pd.to_datetime("2100-01-01"))
                    elif key == Configuration.DATE_MAX:
                        self.step.emit("Removing date outliers...")
                        self.data_cleaning_service.drop_date_outliers(column, pd.to_datetime("1900-01-01"), pd.to_datetime(value))
                        self.progress.emit(70)
                    elif key == Configuration.CATEGORIES:
                        self.step.emit("Correcting categories...")
                        if value != "":
                            self.data_cleaning_service.autocorrect_categories(column, value.split()) # TODO: Make note of splitting on whitespace

            self.progress.emit(80)

            # General cleaning
            if self.cleaning_config[Configuration.DELETE_DUPLICATES]:
                self.step.emit("Deleting duplicate records...")
                self.data_cleaning_service.drop_duplicates()

            self.progress.emit(90)

            if self.cleaning_config[Configuration.DROP_MISSING]:
                self.step.emit("Dropping records with missing values...")
                self.data_cleaning_service.drop_missing_all()
            elif self.cleaning_config[Configuration.IMPUTE_MISSING_MEAN]:
                self.step.emit("Imputing missing values with mean...")
                self.data_cleaning_service.impute_missing_mean_all()
            elif self.cleaning_config[Configuration.IMPUTE_MISSING_MEDIAN]:
                self.step.emit("Imputing missing values with median...")
                self.data_cleaning_service.impute_missing_median_all()

            self.progress.emit(95)
            self.step.emit("Generating cleaning script...")
            self.data_cleaning_service.generate_cleaning_script(self.cleaning_config)

            self.progress.emit(100)
            self.finished.emit(True)

        except Exception as e:
            self.error.emit(f"Error cleaning data: {str(e)}")
            self.finished.emit(False)
