from abc import ABC, abstractmethod
from navigation import Screen

class ViewModel(ABC):
    @property
    @abstractmethod
    def nav_destination(self) -> Screen:
        """Abstract property for navigation destination"""
        pass

    @abstractmethod
    def set_nav_destination(self, destination: Screen):
        """Abstract setter for navigation destination"""
        pass
