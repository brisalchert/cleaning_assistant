import random
import string

import pytest
import pandas as pd
from model import DataModel
from services.data_cleaning_service import DataCleaningService
from tests.helper_functions import generate_random_dataframe
from utils import Configuration


@pytest.fixture
def data_model(tmp_path) -> DataModel:
    """Create a DataModel with generated realistic data."""
    df = generate_random_dataframe()
    table_name = "test_table"
    model = DataModel()
    model.set_database({table_name: df})
    return model

@pytest.fixture
def service(data_model) -> DataCleaningService:
    svc = DataCleaningService(data_model)
    svc.set_and_retrieve_table("test_table")
    return svc

def test_calculate_missingness(service):
    missing_int = service.calculate_missingness("int_col")
    assert missing_int > 0

@pytest.mark.parametrize("col, dtype", [
    ("int_col", "Int64"),
    ("float_col", "Float64"),
    ("datetime_col", "datetime64[ns]"),
])
def test_set_data_type(service, col, dtype):
    changed = service.set_data_type(col, dtype)
    assert changed in (0, 1)
    assert str(service.get_data_type(col)) == dtype

def test_impute_missing_mean(service):
    before = service.calculate_missingness("float_col")
    imputed = service.impute_missing_mean("float_col")
    after = service.calculate_missingness("float_col")
    assert imputed == before - after
    assert after == 0

def test_impute_missing_median(service):
    before = service.calculate_missingness("float_col")
    imputed = service.impute_missing_median("float_col")
    after = service.calculate_missingness("float_col")
    assert imputed == before - after
    assert after == 0

def test_impute_missing_mode(service):
    before = service.calculate_missingness("category_col")
    imputed = service.impute_missing_mode("category_col")
    after = service.calculate_missingness("category_col")
    assert imputed == before - after
    assert after == 0

def test_standardize(service):
    service.standardize("float_col")
    new_mean = service._table["float_col"].mean()
    new_std = service._table["float_col"].std()
    assert abs(new_mean) < 1e-6
    assert abs(new_std - 1) < 1e-6

def test_drop_missing_and_all(service):
    before = service.get_table_length()
    dropped = service.drop_missing("int_col")
    assert dropped >= 0
    dropped_all = service.drop_missing_all()
    assert dropped_all >= 0
    assert service.get_table_length() <= before

def test_clean_categories(service):
    # Remove missing values to avoid NaN issues
    service._table = service._table.dropna(subset=["category_col"]).copy()

    correction_map = {}
    new_category_names = set()
    for category in service._table["category_col"].cat.categories:
        random_name = "".join(random.choices(string.ascii_letters, k=4))
        correction_map[category] = random_name
        new_category_names.add(random_name)

    changed = service.clean_categories("category_col", correction_map)
    assert changed > 0

    updated_categories = set(service._table["category_col"].cat.categories)
    assert updated_categories == new_category_names

def test_autocorrect_categories(service):
    # Remove missing values to avoid NaN issues
    service._table = service._table.dropna(subset=["category_col"]).copy()

    corrected_categories = []
    for category in service._table["category_col"].cat.categories:
        # Append a random letter to create a "typo" or altered version
        altered = category + random.choice(string.ascii_letters)
        corrected_categories.append(altered)

    changed_auto = service.autocorrect_categories("category_col", corrected_categories)
    assert changed_auto > 0

    new_categories = service._table["category_col"].cat.categories
    assert set(new_categories) == set(corrected_categories)

def test_trim_and_truncate_strings(service):
    service._table["string_col"] = service._table["string_col"].astype(str)
    service._model.set_table(service.table_name, service._table)

    trimmed = service.trim_strings("string_col")
    truncated = service.truncate_strings("string_col", max_length=3)
    assert trimmed >= 0
    assert truncated > 0

def test_rename_column(service):
    old_cols = list(service._table.columns)
    service.rename_column("int_col", "new_int_col")
    new_cols = list(service._table.columns)
    assert "new_int_col" in new_cols
    assert "int_col" not in new_cols
    assert len(old_cols) == len(new_cols)

def test_drop_duplicates(service):
    # Convert any list objects to strings (or tuples)
    for col in service._table.columns:
        if service._table[col].apply(lambda x: isinstance(x, list)).any():
            service._table[col] = service._table[col].apply(lambda x: tuple(x) if isinstance(x, list) else x)

    # Add duplicate row to test
    duplicated_row = service._table.iloc[0]

    # Filter out columns that are all NA in the row
    non_na_columns = duplicated_row.dropna().index
    filtered_row_df = duplicated_row[non_na_columns].to_frame().T

    service._table = pd.concat([service._table, filtered_row_df], ignore_index=True)
    service._model.set_table(service.table_name, service._table)

    dropped = service.drop_duplicates()
    assert dropped > 0

def test_get_outliers_and_drop_outliers(service):
    outliers = service.get_outliers("float_col")
    assert isinstance(outliers, pd.DataFrame)

    dropped = service.drop_outliers("float_col")
    assert dropped >= 0

def test_drop_standard_outliers(service):
    dropped = service.drop_standard_outliers("float_col", upper=True)
    assert dropped >= 0
    dropped = service.drop_standard_outliers("float_col", lower=True)
    assert dropped >= 0
    dropped = service.drop_standard_outliers("float_col", upper=True, lower=True)
    assert dropped >= 0

def test_drop_date_outliers(service):
    dropped = service.drop_date_outliers("datetime_col")
    assert dropped >= 0

def test_generate_and_set_cleaning_script(service):
    config = {
        Configuration.COLUMNS: {},
        Configuration.DELETE_DUPLICATES: False,
        Configuration.DROP_MISSING: False,
        Configuration.IMPUTE_MISSING_MEAN: False,
        Configuration.IMPUTE_MISSING_MEDIAN: False
    }
    service.generate_cleaning_script(config)
    assert service.cleaning_script is not None
    assert "# CLEANING ASSISTANT SCRIPT FILE" in service.cleaning_script

def test_set_cleaning_script_and_save(tmp_path, service):
    script_content = "# CLEANING ASSISTANT SCRIPT FILE\nprint('Hello')"
    service.set_cleaning_script(script_content)
    assert service.cleaning_script == script_content

    service.save_cleaning_script(str(tmp_path))
    file_path = tmp_path / "cleaning_script.py"
    assert file_path.exists()

def test_apply_cleaning_script(tmp_path, service):
    # Save a simple valid cleaning script file
    script_file = tmp_path / "cleaning_script.py"
    script_file.write_text(
        "import pandas as pd\n"
        "from pathlib import Path\n"
        "from fuzzywuzzy import process\n"
        "def correct_spelling(row, categories: list):\n"
        "\tmatch = process.extractOne(row, categories)\n"
        "\tif match[1] >= 80:\n"
        "\t\treturn match[0]\n"
        "\telse:\n"
        "\t\treturn row\n"
        f"df = pd.read_csv('{service._table_name}.csv')\n"
        f"desktop = Path.home() / 'Desktop'\n"
        f"file_path = desktop / '{service._table_name}.csv'\n"
        f"df.to_csv(file_path, index=False)\n"
        f"print('Output saved to desktop.')\n"
        "# CLEANING ASSISTANT SCRIPT FILE\n"
    )
    # Save the CSV so subprocess can read it
    service._model.get_table(service.table_name).to_csv(f"{service.table_name}.csv", index=False)

    result = service.apply_cleaning_script(str(script_file))
    assert result is True

    # Cleanup CSV created by apply_cleaning_script
    import os
    from pathlib import Path
    file_path = Path.home() / "Desktop"

    if os.path.exists(f"{file_path}/{service.table_name}.csv"):
        os.remove(f"{file_path}/{service.table_name}.csv")
