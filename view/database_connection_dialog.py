from PyQt6 import QtCore
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout, QCheckBox, QLabel, \
    QTabWidget, QFileDialog, QListView, QPushButton, QWidget, QHBoxLayout, QAbstractItemView


def get_database_files():
    return DatabaseConnectionDialog.files

class DatabaseConnectionDialog(QDialog):
    files = []
    list_model = QStandardItemModel()
    using_files = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Database")
        self.setModal(True)

        # Create tab layout for loading from database / file
        self.tab_layout = QTabWidget(self)

        # --- Load from Database ---

        # Create form layout for user input
        database_widget = QWidget(self)
        form_layout = QFormLayout()

        # Input fields
        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("Database Name")
        form_layout.addRow("Database Name", self.db_name_input)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("User")
        form_layout.addRow("User", self.user_input)

        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        form_layout.addRow("Host", self.host_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password", self.password_input)

        self.port_input = QLineEdit()
        self.port_input.setText("5432")
        form_layout.addRow("Port", self.port_input)

        self.save_parameters_checkbox = QCheckBox()
        self.save_parameters_checkbox.setChecked(False)
        form_layout.addRow("Save Parameters?", self.save_parameters_checkbox)

        self.save_parameters_note = QLabel("Parameters are encrypted using symmetric key encryption.")
        form_layout.addRow(self.save_parameters_note)

        # Add stretch between form and buttons
        database_form_stretch = QWidget(self)
        stretch_layout = QVBoxLayout()
        stretch_layout.addStretch()
        database_form_stretch.setLayout(stretch_layout)
        form_layout.addRow(database_form_stretch)

        # Box for dialog buttons
        database_button_box = QDialogButtonBox(QtCore.Qt.Orientation.Horizontal)
        database_button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        database_button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        database_button_box.accepted.connect(self.accept_db)
        database_button_box.rejected.connect(self.reject)
        form_layout.addRow(database_button_box)

        database_widget.setLayout(form_layout)
        self.tab_layout.addTab(database_widget, "Connect to Database")

        # --- Load from File ---

        file_widget = QWidget(self)
        file_layout = QVBoxLayout()
        self.file_label = QLabel("Files selected:")
        self.file_list = QListView()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.file_list.setModel(DatabaseConnectionDialog.list_model)
        self.file_remove_button = QPushButton("Remove Selected Files")
        self.file_select_button = QPushButton("Import Files")
        self.file_button_io_row = QHBoxLayout()
        self.file_button_io_row.addWidget(self.file_remove_button)
        self.file_button_io_row.addWidget(self.file_select_button)

        # Set up file selection
        self.file_select_button.clicked.connect(self.open_files_dialog)
        self.file_remove_button.clicked.connect(self.on_remove_clicked)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_list)
        file_layout.addLayout(self.file_button_io_row)

        # Box for dialog buttons
        file_button_box = QDialogButtonBox(QtCore.Qt.Orientation.Horizontal)
        file_button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        file_button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        file_button_box.accepted.connect(self.accept_file)
        file_button_box.rejected.connect(self.reject)
        file_layout.addWidget(file_button_box)

        file_widget.setLayout(file_layout)
        self.tab_layout.addTab(file_widget, "Load Files")

        # Add tab layout and button box to dialog
        layout = QVBoxLayout()
        layout.addWidget(self.tab_layout)
        self.setLayout(layout)

    def get_connection_details(self):
        return {
            "db_name": self.db_name_input.text(),
            "user": self.user_input.text(),
            "host": self.host_input.text(),
            "password": self.password_input.text(),
            "port": self.port_input.text(),
            "save": self.save_parameters_checkbox.isChecked()
        }

    def open_files_dialog(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(self, "Select Files")

        if file_paths:
            for file_path in file_paths:
                if file_path not in DatabaseConnectionDialog.files:
                    DatabaseConnectionDialog.files.append(file_path)
                    item = QStandardItem(file_path)
                    DatabaseConnectionDialog.list_model.appendRow(item)
            self.file_list.setModel(DatabaseConnectionDialog.list_model)
            self.file_list.updateGeometry()

    def accept_db(self):
        DatabaseConnectionDialog.using_files = False
        self.accept()

    def accept_file(self):
        DatabaseConnectionDialog.using_files = True
        self.accept()

    def remove_file(self, file_item: QStandardItem):
        index = DatabaseConnectionDialog.list_model.indexFromItem(file_item)
        DatabaseConnectionDialog.files.remove(file_item.text())
        DatabaseConnectionDialog.list_model.removeRow(index.row())
        self.file_list.updateGeometry()

    def on_remove_clicked(self):
        selected_files = self.file_list.selectedIndexes()
        list_items = []

        for index in selected_files:
            list_items.append(DatabaseConnectionDialog.list_model.item(index.row()))

        for item in list_items:
            self.remove_file(item)