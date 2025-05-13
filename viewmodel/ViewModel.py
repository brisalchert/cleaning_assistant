from abc import ABC, abstractmethod
from navigation import Screen

class ViewModel(ABC):
    @abstractmethod
    def set_nav_destination(self, destination: Screen):
        """Abstract setter for navigation destination"""
        pass
