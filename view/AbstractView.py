from abc import ABC, abstractmethod
from navigation import NavigationController, Screen
from viewmodel import ViewModel

class AbstractView(ABC):
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
