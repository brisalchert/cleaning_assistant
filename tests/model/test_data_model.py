import pandas as pd

from model import DataModel
from tests.helper_functions import generate_random_dataframe

database = {
    "table_one": generate_random_dataframe(),
    "table_two": generate_random_dataframe(),
    "table_three": generate_random_dataframe()
}

def init_data_model() -> DataModel:
    return DataModel(database)

def test_get_database():
    data_model = init_data_model()
    retrieved_database = data_model.get_database()
    for key, value in retrieved_database.items():
        pd.testing.assert_frame_equal(retrieved_database[key], database[key])

def test_get_table():
    data_model = init_data_model()
    pd.testing.assert_frame_equal(data_model.get_table("table_one"), database["table_one"])

def test_set_database():
    data_model = init_data_model()
    new_database = {
        "table_three": generate_random_dataframe(),
        "table_four": generate_random_dataframe()
    }
    data_model.set_database(new_database)
    retrieved_database = data_model.get_database()
    for key, value in retrieved_database.items():
        pd.testing.assert_frame_equal(retrieved_database[key], new_database[key])

def test_set_table():
    data_model = init_data_model()
    new_table = generate_random_dataframe()
    data_model.set_table("table_two", new_table)
    pd.testing.assert_frame_equal(data_model.get_table("table_two"), new_table)

def test_update_row():
    data_model = init_data_model()
    original_table = database["table_one"]
    row_index = original_table.index[0]
    updated_row = original_table.loc[row_index].copy()

    updated_row["int_col"] = updated_row["int_col"] + 1

    # Make a 1-row DataFrame for updating
    updated_row_df = updated_row.to_frame().T

    data_model.update_row("table_one", updated_row_df)

    updated_table = data_model.get_table("table_one")
    pd.testing.assert_series_equal(updated_table.iloc[row_index], updated_row)
