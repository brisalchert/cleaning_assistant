from abc import ABC, abstractmethod
from pandas import Series


class ModelEditor(ABC):
    @abstractmethod
    def create_row(self, table_name: str, columns: dict) -> bool:
        """Abstract method for creating a new row in a table"""
        pass

    @abstractmethod
    def read_row(self, table_name: str, primary_key: str) -> Series:
        """Abstract method for reading a row from a table"""

    @abstractmethod
    def update_row(self, table_name: str, primary_key: str, columns: dict) -> bool:
        """Abstract method for updating a row in a table"""
        pass

    @abstractmethod
    def delete_row(self, table_name: str, primary_key: str) -> Series:
        """Abstract method for deleting a row from a table"""
        pass
