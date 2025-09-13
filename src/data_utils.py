import pandas as pd
import json


def load_data(file_path: str, file_format: str):
    """Load data from a file, supporting CSV and JSON formats."""
    if file_format == "csv":
        df = pd.read_csv(file_path, dtype=str)
        return df.to_dict(orient="records")
    elif file_format == "json":
        with open(file_path, mode="r", encoding="utf-8") as file:
            return json.load(file)
    else:
        raise ValueError("Unsupported file format. Use 'csv' or 'json'.")
