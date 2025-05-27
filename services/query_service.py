from pandas import DataFrame
from pandasql import sqldf
from model import DataModel
from services import AbstractService


class QueryService(AbstractService):
    @property
    def model(self) -> DataModel:
        return self._model

    @property
    def query(self) -> str:
        return self._query

    @property
    def last_query_result(self) -> DataFrame:
        return self._last_query_result

    def __init__(self, model: DataModel):
        self._model = model
        self._query = None
        self._last_query_result = None

    def set_query(self, query: str):
        self._query = query

    def execute_query(self) -> DataFrame:
        return sqldf(self._query, env=self._model.database)

    def get_last_result(self) -> DataFrame:
        return self._last_query_result
