import sys
from PyQt6.QtWidgets import QApplication
from model import DataModel
from navigation import NavigationController
from services import DatabaseService, DataEditorService, QueryService, DataCleaningService, AnalyticsService
from view import MainView, DataTableView, AutoCleanView, AnalyticsView
from viewmodel import MainViewModel, DataViewerViewModel, AutoCleanViewModel, AnalyticsViewModel

app = QApplication(sys.argv)

nav_controller = NavigationController()

model = DataModel()

# Initialize services
database_service = DatabaseService(model)
data_editor_service = DataEditorService(model)
query_service = QueryService(model)
data_cleaning_service = DataCleaningService(model)
analytics_service = AnalyticsService(model)

# Initialize view models
main_view_model = MainViewModel(database_service, data_editor_service)
data_viewer_view_model = DataViewerViewModel(data_editor_service, query_service)
auto_clean_view_model = AutoCleanViewModel(data_cleaning_service, analytics_service)
analytics_view_model = AnalyticsViewModel(data_cleaning_service, analytics_service)

# Initialize views
main_view = MainView(main_view_model, nav_controller)
data_table_view = DataTableView(data_viewer_view_model, nav_controller)
auto_clean_view = AutoCleanView(auto_clean_view_model, nav_controller)
analytics_view = AnalyticsView(analytics_view_model, nav_controller)

password = input("Enter DB password: ")
print("Loading...")

# Set up data from PostGreSQL database
connection_details = {
    "dbname": "steam_insights",
    "user": "postgres",
    "host": "localhost",
    "password": password,
    "port": 5432
}

main_view_model.load_database(**connection_details)

main_view.show()
sys.exit(app.exec())
