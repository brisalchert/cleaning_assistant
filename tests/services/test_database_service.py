from unittest.mock import Mock, patch, MagicMock, mock_open
from services import DatabaseService

@patch("services.database_service.pd.read_csv")
@patch("builtins.open", new_callable=mock_open, read_data="fake content")
def test_load_from_files_sets_in_data_model(mock_open_func, mock_read_csv):
    # Mock return value for read_csv
    fake_df = MagicMock()
    mock_read_csv.return_value = fake_df

    # Mock model
    model = Mock()
    service = DatabaseService(model)

    csv_config = {
        "sep": ",",
        "escapechar": "\\",
        "quotechar": '"',
        "doublequote": True
    }

    # Fake files
    file_list = ["some/path/table1.csv", "another/path/table2.csv"]

    result = service.load_from_files(file_list, csv_config)

    # Assertions
    assert result is True
    model.set_database.assert_called_once()
    tables_passed = model.set_database.call_args[0][0]
    assert "table1" in tables_passed
    assert "table2" in tables_passed
    assert tables_passed["table1"] is fake_df
    assert tables_passed["table2"] is fake_df

@patch("services.database_service.create_engine")
@patch("services.database_service.pd.read_sql")
def test_load_from_database_sets_data_in_model(mock_read_sql, mock_create_engine):
    dummy_df = MagicMock()
    mock_read_sql.return_value = dummy_df

    # Set up fake result for connection.execute()
    fake_result = [("table1",), ("table2",)]

    mock_connection = MagicMock()
    mock_connection.execute.return_value = fake_result

    # Simulate context manager
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    mock_create_engine.return_value = mock_engine

    model = Mock()
    service = DatabaseService(model)

    connection_details = {
        "db_name": "test_db",
        "user": "user",
        "host": "localhost",
        "password": "pass",
        "port": 5432
    }

    result = service.load_from_database(connection_details)

    assert result is True
    mock_create_engine.assert_called_once()
    model.set_database.assert_called_once()
    tables_passed = model.set_database.call_args[0][0]
    assert "table1" in tables_passed
    assert "table2" in tables_passed
