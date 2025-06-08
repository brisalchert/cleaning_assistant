import pandas as pd
import pytest

from services.analytics_service import AnalyticsService
from model import DataModel


@pytest.fixture
def mock_model():
    class MockModel(DataModel):
        def __init__(self):
            super().__init__()
            self.tables = {}

        def get_table(self, name):
            return self.tables[name]

        def set_table(self, name, df):
            self.tables[name] = df

    return MockModel()

@pytest.fixture
def service(mock_model):
    return AnalyticsService(mock_model)

def test_set_table_and_reset(service, mock_model):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    mock_model.set_table("test_table", df)

    service.set_table("test_table")

    assert service._table_name == "test_table"
    assert service._table.equals(df)
    assert service.statistics == {}
    assert service.plots == {}
    assert service.suggestions == {}
    assert service.analytics_available is False

def test_calculate_missingness_stats(service, mock_model):
    df = pd.DataFrame({"a": [1, None, 3], "b": [None, None, 3]})
    mock_model.set_table("test", df)
    service.set_table("test")

    service.calculate_missingness_stats()
    stats = service.statistics["missingness"]

    assert stats["a"] == pytest.approx(33.33, 0.1)
    assert stats["b"] == pytest.approx(66.66, 0.1)

def test_calculate_category_stats(service, mock_model):
    df = pd.DataFrame({"cat": pd.Series(["a", "b", "a"], dtype="category"), "num": [1, 2, 3]})
    mock_model.set_table("test", df)
    service.set_table("test")

    service.calculate_category_stats()
    stats = service.statistics["categories"]

    assert stats["cat"] == {"a": 2, "b": 1}
    assert "num" not in stats

def test_calculate_outlier_stats(service, mock_model):
    df = pd.DataFrame({"a": [1, 2, 3, 100]})
    mock_model.set_table("test", df)
    service.set_table("test")

    service.calculate_outlier_stats()
    stats = service.statistics["outliers"]

    assert stats["a"]["upper"] == 1
    assert stats["a"]["lower"] == 0

def test_create_missingness_plot_data(service, mock_model):
    df = pd.DataFrame({"a": [1, None, 3]})
    mock_model.set_table("test", df)
    service.set_table("test")

    service.create_missingness_plot_data()
    assert "missingness" in service.plots
    assert service.plots["missingness"].equals(df)

def test_create_outlier_plot_data(service, mock_model):
    df = pd.DataFrame({"a": [1, 2, 3, 4]})
    mock_model.set_table("test", df)
    service.set_table("test")

    service.create_outlier_plot_data()
    assert "outliers" in service.plots
    assert all((0.0 <= v <= 1.0) for v in service.plots["outliers"]["a"])

def test_create_distribution_plot_data(service, mock_model):
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0, None], "b": ["x", "y", "z", "x"]})
    mock_model.set_table("test", df)
    service.set_table("test")

    service.create_distribution_plot_data("a")
    service.create_distribution_plot_data("b")

    assert "a" in service.plots["distributions"]
    assert "b" not in service.plots.get("distributions", {})

def test_generate_suggestions(service):
    service.generate_suggestions()
    suggestions = service.suggestions

    assert "missingness" in suggestions
    assert "outliers" in suggestions
    assert "categories" in suggestions
    assert "distributions" in suggestions
