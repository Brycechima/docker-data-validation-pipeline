import argparse
import sys
import pandas as pd
import pandera as pa
from pandera import Column, Check, DataFrameSchema

# Define strict data governance schema
DatasetSchema = DataFrameSchema({
    "id": Column(int, Check.greater_than(0), unique=True),
    "user_query": Column(str, Check.str_length(min_value=3)),
    "model_response": Column(str, Check.str_length(min_value=1)),
    "accuracy_score": Column(float, Check.in_range(0.0, 1.0)),
    "instruction_adherence": Column(bool),
    "category": Column(str, Check.isin(["reasoning", "coding", "spatial", "multimodal"]))
})

def validate_dataset(filepath: str):
    print(f"[INFO] Ingesting dataset from: {filepath}")
    df = pd.read_csv(filepath)
    
    # Assert missingness rate is below threshold
    null_ratio = df.isnull().mean().mean()
    if null_ratio > 0.05:
        print(f"[ERROR] Null ratio {null_ratio:.2%} exceeds acceptable 5% threshold.")
        sys.exit(1)
        
    try:
        DatasetSchema.validate(df)
        print(f"[SUCCESS] Dataset passed all {len(df)} row schema validations.")
        return True
    except pa.errors.SchemaError as err:
        print(f"[FATAL] Schema validation failed:
{err}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Docker Data Validation Script")
    parser.add_argument("--dataset", required=True, help="Path to CSV dataset")
    args = parser.parse_args()
    validate_dataset(args.dataset)
