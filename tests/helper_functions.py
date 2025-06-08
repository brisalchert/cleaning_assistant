import random
import string

import numpy as np
import pandas as pd
from pandas import DataFrame


def generate_random_dataframe(n_rows: int = 100, nan_prob: float = 0.1, seed: int = None) -> DataFrame:
    rng = np.random.default_rng(seed)

    def maybe_na(values, na_value):
        return [v if rng.random() > nan_prob else na_value for v in values]

    def random_string(length=8):
        return "".join(random.choices(string.ascii_letters, k=length))

    def random_object():
        # Mix of different data types
        choices = [
            random_string(),
            [random.randint(1,5) for _ in range(3)],
            random.randint(1, 100),
            None
        ]
        return random.choice(choices)

    int_values = maybe_na(rng.integers(low=0, high=100, size=n_rows).tolist(), pd.NA)
    float_values = maybe_na(rng.normal(50, 15, size=n_rows).tolist(), np.nan)
    bool_values = maybe_na(rng.choice([True, False], size=n_rows).tolist(), pd.NA)
    datetime_values = maybe_na(
        pd.to_datetime(
            rng.integers(pd.Timestamp("2020-01-01").value, pd.Timestamp("2025-01-01").value, size=n_rows)
        ).tolist(), pd.NaT
    )
    string_values = maybe_na([random_string() for _ in range(n_rows)], pd.NA)
    category_values = maybe_na(rng.choice(["Apple", "Banana", "Carrot", "Durian", "Edamame", "Fruit"], size=n_rows).tolist(), pd.NA)
    object_values = maybe_na([random_object() for _ in range(n_rows)], None)

    df = pd.DataFrame({
        "int_col": pd.Series(int_values, dtype="Int64"),
        "float_col": pd.Series(float_values, dtype="Float64"),
        "bool_col": pd.Series(bool_values, dtype="boolean"),
        "datetime_col": pd.Series(datetime_values, dtype="datetime64[ns]"),
        "string_col": pd.Series(string_values, dtype="string"),
        "category_col": pd.Series(category_values, dtype="category"),
        "object_col": pd.Series(object_values, dtype="object"),
    })

    return df
