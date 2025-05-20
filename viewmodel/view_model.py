from abc import ABC, abstractmethod, ABCMeta
from PyQt6.QtCore import QObject
from navigation import Screen


class MetaQObjectABC(type(QObject), ABCMeta):
    pass

class ViewModel(QObject, metaclass=MetaQObjectABC):
    @abstractmethod
    def set_nav_destination(self, destination: Screen):
        """Abstract setter for navigation destination"""
        pass
