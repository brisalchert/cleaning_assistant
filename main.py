import sys
from PyQt6.QtWidgets import QApplication
from model import DataModel
from navigation import NavigationController
from services import DatabaseService, DataEditorService
from view import MainView
from viewmodel import MainViewModel

app = QApplication(sys.argv)

nav_controller = NavigationController()

model = DataModel()

database_service = DatabaseService(model)
data_editor_service = DataEditorService(model)

main_view_model = MainViewModel(database_service, data_editor_service)
main_view = MainView(main_view_model, nav_controller)

main_view.show()
sys.exit(app.exec())
