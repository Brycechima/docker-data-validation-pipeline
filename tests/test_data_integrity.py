import pytest
import pandas as pd
from src.validate import DatasetSchema

@pytest.fixture
def dataset():
    return pd.read_csv("data/sample_dataset.csv")

def test_schema_conformance(dataset):
    """Verify that all records strictly adhere to the defined Pandera schema."""
    validated = DatasetSchema.validate(dataset)
    assert validated is not None

def test_no_null_critical_fields(dataset):
    """Verify zero null values in critical identity and reasoning fields."""
    assert dataset["id"].isnull().sum() == 0
    assert dataset["user_query"].isnull().sum() == 0
    assert dataset["accuracy_score"].isnull().sum() == 0

def test_accuracy_score_bounds(dataset):
    """Ensure all model accuracy scores fall within [0.0, 1.0]."""
    assert (dataset["accuracy_score"] >= 0.0).all()
    assert (dataset["accuracy_score"] <= 1.0).all()
