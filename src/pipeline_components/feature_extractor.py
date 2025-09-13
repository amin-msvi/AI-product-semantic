from typing import Dict, List, Any
import logging


class FeatureExtractor:
    """Extracts key features from normalized product data."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract(self, product: Dict[str, Any]) -> List[str]:
        """
        Extract key features from a normalized product record.

        Args:
            product: Normalized product dictionary

        Returns:
            List of extracted feature strings
        """
        text = f"{product.get('title', '')} {product.get('description', '')}".lower()
        features = []

        # Material features
        materials = ["cotton", "organic", "denim", "wool"]
        for material in materials:
            if material in text:
                features.append(material)

        # Style features
        if "slim" in text:
            features.append("slim_fit")
        if "stretch" in text:
            features.append("stretchy")

        # Color features
        colors = ["white", "blue", "black"]
        for color in colors:
            if color in text:
                features.append(f"{color}_color")

        self.logger.info(
            f"Extracted {len(features)} features for product ID: {product.get('id', 'N/A')}"
        )
        return features
