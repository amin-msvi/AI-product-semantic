import pandas as pd
import json
from pathlib import Path
from typing import Union, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading data from various file formats with validation."""

    SUPPORTED_FORMATS = {"csv", "json"}

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_data(
        self, file_path: Union[str, Path], file_format: str
    ) -> Union[List[Dict], Dict]:
        file_path = Path(file_path)

        if file_format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format '{file_format}'. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.logger.info(f"Loading {file_format.upper()} data from {file_path}")

        try:
            if file_format == "csv":
                return self._load_csv(file_path)
            elif file_format == "json":
                return self._load_json(file_path)
        except Exception as e:
            self.logger.error(f"Error loading {file_format} file {file_path}: {str(e)}")
            raise

    def _load_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load CSV file and convert to list of dictionaries."""
        df = pd.read_csv(file_path, dtype=str)
        df = df.fillna("")  # Replace NaN with empty strings
        data = df.to_dict(orient="records")
        self.logger.info(f"Loaded {len(data)} records from CSV")
        return data

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        with open(file_path, mode="r", encoding="utf-8") as file:
            data = json.load(file)
        self.logger.info(f"Loaded JSON data with {len(data)} top-level keys")
        return data

    def save_json(
        self, data: Union[Dict, List], file_path: Union[str, Path], indent: int = 2
    ) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        self.logger.info(f"Saved data to {file_path}")
