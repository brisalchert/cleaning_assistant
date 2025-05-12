from abc import ABC, abstractmethod
from view import Screen

class ViewModel(ABC):
    @property
    @abstractmethod
    def nav_destination(self) -> Screen:
        """Abstract property for navigation destination"""
        pass

    @nav_destination.setter
    @abstractmethod
    def nav_destination(self, value: Screen):
        """Abstract setter for navigation destination"""
