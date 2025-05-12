from abc import ABC, abstractmethod
from model import DataModel

class AbstractService(ABC):
    @property
    @abstractmethod
    def model(self) -> DataModel:
        """Abstract attribute for data model"""
        pass

    @model.setter
    @abstractmethod
    def model(self, value: DataModel):
        """Abstract setter for data model"""
        pass
