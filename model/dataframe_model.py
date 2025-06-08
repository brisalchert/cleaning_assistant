from PyQt6.QtCore import QAbstractTableModel, Qt, QVariant, QModelIndex
from pandas import DataFrame


class DataFrameModel(QAbstractTableModel):
    def __init__(self, dataframe: DataFrame):
        super().__init__()
        self._dataframe = dataframe
        self._editable = False

    # Override QAbstractTableModel methods

    def rowCount(self, parent=None):
        return self._dataframe.shape[0]

    def columnCount(self, parent=None):
        return self._dataframe.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid() and role == Qt.ItemDataRole.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])
        return QVariant()

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if self._editable and role == Qt.ItemDataRole.EditRole:
            self._dataframe.iat[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QModelIndex):
        base_flags = super().flags(index)
        if self._editable:
            return base_flags | Qt.ItemFlag.ItemIsEditable
        else:
            return base_flags & ~Qt.ItemFlag.ItemIsEditable

    def update_editing(self, editable: bool):
        self._editable = editable
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return QVariant()
        if orientation == Qt.Orientation.Horizontal:
            return str(self._dataframe.columns[section])
        elif orientation == Qt.Orientation.Vertical:
            return str(self._dataframe.index[section])
        return QVariant()

    def get_dataframe(self) -> DataFrame:
        return self._dataframe

    def set_dataframe(self, dataframe: DataFrame):
        self.beginResetModel()
        self._dataframe = dataframe
        self.endResetModel()
