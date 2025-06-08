import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from services import QueryService


@pytest.fixture
def mock_model():
    return MagicMock()

@pytest.fixture
def service(mock_model):
    return QueryService(mock_model)

def test_set_query_sets_internal_value(service):
    query = "SELECT * FROM users"
    service.set_query(query)
    assert service.query == query

@patch("services.query_service.sqldf")
def test_execute_query_calls_sqldf_with_correct_env(mock_sqldf, service, mock_model):
    query = "SELECT * FROM users"
    mock_df = pd.DataFrame([{"id": 1, "name": "Alice"}])
    mock_sqldf.return_value = mock_df
    mock_model.get_database.return_value = {"users": mock_df}

    service.set_query(query)
    result = service.execute_query()

    mock_sqldf.assert_called_once_with(query, env={"users": mock_df})
    assert result.equals(mock_df)

def test_get_last_result_returns_stored_value(service):
    df = pd.DataFrame([{"x": 1}])
    service._last_query_result = df
    assert service.get_last_result().equals(df)

# Integration test with real data
def test_execute_query_with_real_dataframe(service, mock_model):
    df = pd.DataFrame([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ])
    mock_model.get_database.return_value = {"users": df}

    service.set_query("SELECT name FROM users WHERE id = 1")
    result = service.execute_query()

    assert list(result["name"]) == ["Alice"]
