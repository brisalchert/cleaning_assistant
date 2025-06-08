from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
from services import DataEditorService


@pytest.fixture
def mock_model():
    model = MagicMock()
    return model

@pytest.fixture
def editor(mock_model):
    return DataEditorService(mock_model)

def test_update_row_pushes_diff_to_undo_stack(editor, mock_model):
    table_name = "users"
    old_df = pd.DataFrame([{"id": 1, "name": "Alice"}])
    new_df = pd.DataFrame([{"id": 1, "name": "Bob"}])

    mock_model.get_table.return_value = old_df.copy()
    mock_model.update_row.return_value = True

    result = editor.update_row(table_name, 0, new_df)

    assert result is True
    assert len(editor.undo_stack) == 1
    assert editor.undo_stack[0][0]["old_value"] == "Alice"
    assert editor.undo_stack[0][0]["new_value"] == "Bob"

def test_undo_change_applies_old_value(editor, mock_model):
    table_name = "users"
    diff = [{"table": table_name, "row": 0, "column": "name", "old_value": "Alice", "new_value": "Bob"}]

    df = pd.DataFrame([{"id": 1, "name": "Bob"}])
    mock_model.get_table.return_value = df.copy()

    editor.undo_stack.append(diff)

    editor.undo_change()

    assert editor.redo_stack[-1] == diff
    mock_model.set_table.assert_called_once()
    updated_df = mock_model.set_table.call_args[0][1]
    assert updated_df.at[0, "name"] == "Alice"

def test_redo_change_applies_new_value(editor, mock_model):
    table_name = "users"
    diff = [{"table": table_name, "row": 0, "column": "name", "old_value": "Alice", "new_value": "Bob"}]

    df = pd.DataFrame([{"id": 1, "name": "Alice"}])
    mock_model.get_table.return_value = df.copy()

    editor.redo_stack.append(diff)

    editor.redo_change()

    assert editor.undo_stack[-1] == diff
    mock_model.set_table.assert_called_once()
    updated_df = mock_model.set_table.call_args[0][1]
    assert updated_df.at[0, "name"] == "Bob"

@patch("services.data_editor_service.Path.mkdir")
@patch("services.data_editor_service.Path.write_text")
@patch("services.data_editor_service.DataFrame.to_csv")
def test_export_data_creates_files(mock_to_csv, mock_write, mock_mkdir, editor, mock_model):
    df = pd.DataFrame([{"id": 1, "name": "Alice"}])
    mock_model.get_database.return_value = {"users": df}

    result = editor.export_data("mock_dir")

    assert result is True
    mock_to_csv.assert_called_once()
    mock_mkdir.assert_called_once()

def test_get_undo_available(editor):
    assert not editor.get_undo_available()
    editor.undo_stack.append([{"some": "change"}])
    assert editor.get_undo_available()

def test_get_redo_available(editor):
    assert not editor.get_redo_available()
    editor.redo_stack.append([{"some": "change"}])
    assert editor.get_redo_available()

def test_set_table_sets_current_table(editor, mock_model):
    df = pd.DataFrame([{"id": 1}])
    mock_model.get_table.return_value = df
    editor.set_table("users")
    assert editor.get_current_table().equals(df)
