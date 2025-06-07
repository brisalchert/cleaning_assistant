from PyQt6.QtCore import Qt, QSize
import missingno as msno
import seaborn as sns
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QLabel, QPushButton, QHBoxLayout, \
    QStackedWidget, QComboBox, QLayout, QFrame
from pandas import DataFrame, Series

from navigation import NavigationController
from utils import MplCanvas, Operation
from view import AbstractView
from viewmodel import AnalyticsViewModel


class AnalyticsView(AbstractView):
    @property
    def view_model(self):
        return self._view_model

    @property
    def nav_controller(self):
        return self._nav_controller

    def __init__(self, view_model: AnalyticsViewModel, nav_controller: NavigationController):
        super().__init__()
        self._view_model = view_model
        self._nav_controller = nav_controller

        # Set up view header
        self.header_label = QLabel("Cleaning Analytics")
        self.header_label.setFont(QFont(self.font, 24))
        self.header_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.stats_export_button = QPushButton("Save Statistics")
        self.stats_export_button.setFont(QFont(self.font, 14))
        self.stats_export_button.setEnabled(False)
        self.stats_export_button.clicked.connect(self.export_stats)
        self.plots_export_button = QPushButton("Save Plots")
        self.plots_export_button.setFont(QFont(self.font, 14))
        self.plots_export_button.setEnabled(False)
        self.plots_export_button.clicked.connect(self.export_plots)

        self.header_group = QWidget()
        self.header_group.setLayout(QHBoxLayout())
        self.header_group.layout().addWidget(self.header_label)
        self.header_group.layout().addStretch()
        self.header_group.layout().addWidget(self.stats_export_button)
        self.header_group.layout().addWidget(self.plots_export_button)

        # Set up scroll area for analytics
        self.analytics_container = QWidget()
        self.analytics_container.setLayout(QVBoxLayout())
        self.analytics_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.no_analytics_container = QWidget()
        self.no_analytics_container.setLayout(QVBoxLayout())
        self.no_analytics_container.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_analytics_label = QLabel("No Analytics Available")
        self.no_analytics_label.setFont(QFont(self.font, 24, QFont.Weight.Bold))
        self.no_analytics_description = QLabel("Run the auto-cleaning tool to generate analytics!")
        self.no_analytics_description.setFont(QFont(self.font, 14))
        self.no_analytics_container.layout().addWidget(self.no_analytics_label)
        self.no_analytics_container.layout().addWidget(self.no_analytics_description)

        # Stacked widget for loaded/not loaded
        self.analytics_container_stack = QStackedWidget()
        self.analytics_container_stack.addWidget(self.no_analytics_container)
        self.analytics_container_stack.addWidget(self.analytics_container)
        self.analytics_container_stack.setMaximumWidth(900)
        self.analytics_container_stack.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)

        analytics_scroll_area = QScrollArea()
        analytics_scroll_area.setWidget(self.analytics_container_stack)
        analytics_scroll_area.setWidgetResizable(True)
        analytics_scroll_area.setMinimumWidth(1200)
        analytics_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Missingness stats
        self.missingness_container = QWidget()
        self.missingness_container.setLayout(QVBoxLayout())
        self.missingness_container.layout().setContentsMargins(10, 10, 10, 10)
        self.missingness_label = QLabel("Missingness Statistics")
        self.missingness_label.setFont(QFont(self.font, 14))
        self.missingness_text = QLabel()
        self.missingness_text.setWordWrap(True)
        self.missingness_text.setFont(QFont(self.font, 12))
        self.missingness_text.setContentsMargins(10, 10, 10, 10)
        self.missingness_plot = MplCanvas()

        self.drop_missing_button = QPushButton("Drop Missing")
        self.impute_missing_mean_button = QPushButton("Impute Mean")
        self.impute_missing_median_button = QPushButton("Impute Median")
        self.impute_missing_mode_button = QPushButton("Impute Mode")

        self.missingness_button_row = QWidget()
        self.missingness_button_row.setLayout(QHBoxLayout())
        self.missingness_button_row.layout().addWidget(self.drop_missing_button)
        self.missingness_button_row.layout().addWidget(self.impute_missing_mean_button)
        self.missingness_button_row.layout().addWidget(self.impute_missing_median_button)
        self.missingness_button_row.layout().addWidget(self.impute_missing_mode_button)

        for button in [
            self.drop_missing_button,
            self.impute_missing_mean_button,
            self.impute_missing_median_button,
            self.impute_missing_mode_button
        ]:
            button.setFont(QFont(self.font, 12))

        self.missingness_container.layout().addWidget(self.missingness_label)
        self.missingness_container.layout().addWidget(self.missingness_text)
        self.missingness_container.layout().addWidget(self.missingness_plot)
        self.missingness_container.layout().addWidget(self.missingness_button_row)

        self.analytics_container.layout().addWidget(self.missingness_container)

        missingness_separator = QFrame()
        missingness_separator.setFrameShape(QFrame.Shape.HLine)
        missingness_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.analytics_container.layout().addWidget(missingness_separator)

        # Outlier stats
        self.outlier_container = QWidget()
        self.outlier_container.setLayout(QVBoxLayout())
        self.outlier_container.layout().setContentsMargins(10, 10, 10, 10)
        self.outlier_label = QLabel("Outlier Statistics")
        self.outlier_label.setFont(QFont(self.font, 14))
        self.outlier_text = QLabel()
        self.outlier_text.setWordWrap(True)
        self.outlier_text.setFont(QFont(self.font, 12))
        self.outlier_text.setContentsMargins(10, 10, 10, 10)
        self.outlier_plot = MplCanvas()

        self.outlier_column_label = QLabel("Column:")
        self.outlier_column_label.setFont(QFont(self.font, 12))
        self.outlier_column_selector = QComboBox()
        self.outlier_column_selector.setFont(QFont(self.font, 12))
        self.drop_upper_button = QPushButton("Drop Upper Outliers")
        self.drop_upper_button.setFont(QFont(self.font, 12))
        self.drop_lower_button = QPushButton("Drop Lower Outliers")
        self.drop_lower_button.setFont(QFont(self.font, 12))

        self.outlier_button_row = QWidget()
        self.outlier_button_row.setLayout(QHBoxLayout())
        self.outlier_button_row.layout().addStretch()
        self.outlier_button_row.layout().addWidget(self.outlier_column_label)
        self.outlier_button_row.layout().addWidget(self.outlier_column_selector)
        self.outlier_button_row.layout().addWidget(self.drop_upper_button)
        self.outlier_button_row.layout().addWidget(self.drop_lower_button)

        self.outlier_container.layout().addWidget(self.outlier_label)
        self.outlier_container.layout().addWidget(self.outlier_text)
        self.outlier_container.layout().addWidget(self.outlier_plot)
        self.outlier_container.layout().addWidget(self.outlier_button_row)

        self.analytics_container.layout().addWidget(self.outlier_container)

        outlier_separator = QFrame()
        outlier_separator.setFrameShape(QFrame.Shape.HLine)
        outlier_separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.analytics_container.layout().addWidget(outlier_separator)

        # Distribution stats
        self.distribution_container = QWidget()
        self.distribution_container.setLayout(QVBoxLayout())
        self.distribution_container.layout().setContentsMargins(10, 10, 10, 10)
        self.distribution_label = QLabel("Distribution Statistics")
        self.distribution_label.setFont(QFont(self.font, 14))
        self.distribution_text = QLabel()
        self.distribution_text.setWordWrap(True)
        self.distribution_text.setFont(QFont(self.font, 12))
        self.distribution_text.setContentsMargins(10, 10, 10, 10)
        self.distribution_plots = {}

        self.distribution_container.layout().addWidget(self.distribution_label)
        self.distribution_container.layout().addWidget(self.distribution_text)

        self.analytics_container.layout().addWidget(self.distribution_container)

        # Navigation
        self.setup_navigation()

        # Main Layout
        self.analytics_layout = QVBoxLayout()
        self.analytics_layout.addWidget(self._nav_bar)
        self.analytics_layout.addWidget(self.header_group)
        self.analytics_layout.addWidget(analytics_scroll_area)

        # ----------------------------------------------------------------------
        # --- Initialize UI ---
        # ----------------------------------------------------------------------

        # Initialize UI with the layout
        self.setLayout(self.analytics_layout)

        # Connect ViewModel to UI
        self._view_model.nav_destination_changed.connect(self.navigate)
        self._view_model.stats_updated.connect(self.update_stats)
        self._view_model.plot_data_updated.connect(self.update_plots)
        self._view_model.suggestions_updated.connect(self.update_suggestions)
        self._view_model.analytics_updated.connect(self.update_analytics)

        # Connect navigation controller to UI
        self._nav_controller.nav_destination_changed.connect(self.update_nav_bar)

    def setup_navigation(self):
        super().setup_navigation()
        self._nav_analytics.setChecked(True)

    def update_stats(self, stats: dict):
        pass

    def update_plots(self, plot_data: dict):
        # Update missingness plot
        if "missingness" in plot_data:
            layout = self.missingness_container.layout()

            # Find index of missingness plot
            target_index = self.get_plot_index(self.missingness_plot, layout)

            if target_index == -1:
                print("Warning: missingness_plot not found in layout")
                return

            self.create_missingness_plot(plot_data["missingness"], target_index)

        # Update outlier plot
        if "outliers" in plot_data:
            layout = self.outlier_container.layout()

            # Find index of outlier plot
            target_index = self.get_plot_index(self.outlier_plot, layout)

            if target_index == -1:
                print("Warning: outlier_plot not found in layout")
                return

            # Melt DataFrame for proper plotting format
            df_melted = plot_data["outliers"].melt(var_name="column", value_name="value").dropna()
            self.create_outlier_plot(df_melted, target_index)

            # Update column selector options
            self.outlier_column_selector.clear()

            for column in plot_data["outliers"].columns:
                self.outlier_column_selector.addItem(column)

        # Update distribution plots
        if "distributions" in plot_data:
            layout = self.distribution_container.layout()

            for column, series in plot_data["distributions"].items():
                self.create_distribution_plot(column, series)

                standardize_button = QPushButton(f"Standardize \"{column}\" Distribution")
                standardize_button.setFont(QFont(self.font, 12))
                standardize_button.clicked.connect(lambda: self._view_model.apply_suggestion(Operation.STANDARDIZE, column))

                layout.addWidget(self.distribution_plots[column])
                layout.addWidget(standardize_button)

    def update_suggestions(self, suggestions: dict):
        # Update missingness suggestions
        if "missingness" in suggestions:
            self.missingness_text.setText(suggestions["missingness"])

        # Update outlier suggestions
        if "outliers" in suggestions:
            self.outlier_text.setText(suggestions["outliers"])

        # Update distributions suggestions
        if "distributions" in suggestions:
            self.distribution_text.setText(suggestions["distributions"])

        # Update category suggestions
        if "categories" in suggestions:
            # self.categories_text.setText(suggestions["categories"])
            pass

    def update_analytics(self, available: bool):
        if available:
            self.analytics_container_stack.setCurrentIndex(1)
        else:
            self.analytics_container_stack.setCurrentIndex(0)

    def get_plot_index(self, plot_widget: QWidget, layout: QLayout):
        index = -1

        for i in range(layout.count()):
            if layout.itemAt(i).widget() == plot_widget:
                index = i
                break

        return index

    def create_missingness_plot(self, df: DataFrame, layout_index: int):
        layout = self.missingness_container.layout()

        # Remove old plot
        old_widget = self.missingness_plot
        layout.removeWidget(old_widget)
        old_widget.setParent(None)
        old_widget.deleteLater()

        # Create new plot
        canvas = MplCanvas()
        ax = canvas.ax
        msno.matrix(df, ax=ax, sparkline=False)
        ax.set_title("Missingness Distribution per Column")
        canvas.draw()

        # Add plot to layout
        self.missingness_plot = canvas
        layout.insertWidget(layout_index, self.missingness_plot)

    def create_outlier_plot(self, df: DataFrame, layout_index: int):
        layout = self.outlier_container.layout()

        # Remove old plot
        old_widget = self.outlier_plot
        layout.removeWidget(old_widget)
        old_widget.setParent(None)
        old_widget.deleteLater()

        # Create new plot
        canvas = MplCanvas()
        ax = canvas.ax
        sns.boxplot(x="column", y="value", data=df, showfliers=True, ax=ax)
        ax.set_title("Boxplot for Outliers (Numeric, Dates, and String Lengths [Normalized])")
        ax.tick_params(axis='x', labelrotation=45)
        canvas.draw()

        # Add plot to layout
        self.outlier_plot = canvas
        layout.insertWidget(layout_index, self.outlier_plot)

    def create_distribution_plot(self, column: str, distribution: Series):
        # Create new plot
        canvas = MplCanvas()
        ax = canvas.ax
        sns.histplot(distribution, kde=False, bins=30, ax=ax)
        ax.set_title(f"Distribution Plot for {column.title()}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        canvas.draw()

        # Add plot to plot dictionary
        self.distribution_plots[column] = canvas

    def export_stats(self):
        # TODO: Implement export_stats
        pass

    def export_plots(self, plot_name: str):
        # TODO: Implement export_plots
        pass
