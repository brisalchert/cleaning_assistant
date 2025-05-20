from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout


class DatabaseConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Database")
        self.setModal(True)

        # Create form layout for user input
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

        # Box for dialog buttons
        button_box = QDialogButtonBox(QtCore.Qt.Orientation.Horizontal)
        button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Add form layout and button box to dialog
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_connection_details(self):
        return {
            "db_name": self.db_name_input.text(),
            "user": self.user_input.text(),
            "host": self.host_input.text(),
            "password": self.password_input.text(),
            "port": self.port_input.text(),
        }
