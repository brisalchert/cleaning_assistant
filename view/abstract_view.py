from abc import abstractmethod, ABCMeta

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QButtonGroup, QPushButton, QHBoxLayout

from navigation import NavigationController, Screen
from viewmodel import ViewModel


class MetaQWidgetABC(type(QWidget), ABCMeta):
    pass

class AbstractView(QWidget, metaclass=MetaQWidgetABC):
    @abstractmethod
    def __init__(self):
        super().__init__()
        # Initialize instance attributes
        self._nav_bar = None
        self._nav_main = None
        self._nav_auto_clean = None
        self._nav_analytics = None
        self._nav_button_group = None
        self.font = "Cascadia Code"

    @property
    @abstractmethod
    def view_model(self):
        """Abstract property for view model"""
        pass

    @property
    @abstractmethod
    def nav_controller(self):
        """Abstract property for navigation controller"""
        pass

    @view_model.setter
    @abstractmethod
    def view_model(self, value: ViewModel):
        """Abstract setter for view model"""
        pass

    @nav_controller.setter
    @abstractmethod
    def nav_controller(self, value: NavigationController):
        """Abstract setter for navigation controller"""
        pass

    def navigate(self, screen: Screen):
        """Navigate to a new screen"""
        self.nav_controller.navigate(screen)

    def update_nav_bar(self, screen: Screen):
        """Update navigation bar selection"""
        if self._nav_bar:
            # Temporarily disable exclusivity to uncheck all buttons
            self._nav_button_group.setExclusive(False)
            for button in self._nav_button_group.buttons():
                button.setChecked(False)
            self._nav_button_group.setExclusive(True)

            # Check button for current screen if applicable
            match screen:
                case Screen.MAIN:
                    self._nav_main.setChecked(True)
                case Screen.AUTO_CLEAN:
                    self._nav_auto_clean.setChecked(True)
                case Screen.ANALYTICS:
                    self._nav_analytics.setChecked(True)
                case Screen.DATA_TABLE:
                    pass

    def setup_navigation(self):
        self._nav_bar = QWidget()
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        # Create navigation buttons
        self._nav_main = QPushButton("Main View")
        self._nav_auto_clean = QPushButton("Auto Clean")
        self._nav_analytics = QPushButton("Analytics")

        # Create button group for exclusive selection
        self._nav_button_group = QButtonGroup(self)
        self._nav_button_group.addButton(self._nav_main)
        self._nav_button_group.addButton(self._nav_auto_clean)
        self._nav_button_group.addButton(self._nav_analytics)
        self._nav_button_group.setExclusive(True)

        # Add buttons to layout
        nav_layout.addWidget(self._nav_main)
        nav_layout.addWidget(self._nav_auto_clean)
        nav_layout.addWidget(self._nav_analytics)
        nav_layout.addStretch()

        self._nav_bar.setLayout(nav_layout)

        # Apply style to navigation buttons
        for button in [self._nav_main, self._nav_auto_clean, self._nav_analytics]:
            button.setCheckable(True)
            button.setContentsMargins(5, 5, 5, 5)
            button.setFont(QFont("Cascadia Code", 14))

        # Connect navigation signals to view model
        self._nav_main.clicked.connect(lambda: self.view_model.set_nav_destination(Screen.MAIN))
        self._nav_auto_clean.clicked.connect(lambda: self.view_model.set_nav_destination(Screen.AUTO_CLEAN))
        self._nav_analytics.clicked.connect(lambda: self.view_model.set_nav_destination(Screen.ANALYTICS))
