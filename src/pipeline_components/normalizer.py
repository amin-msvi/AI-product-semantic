import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
import pandas as pd


@dataclass
class NormalizationConfig:
    """Configuration for product data normalization."""

    max_title_length: int = 150
    max_description_length: int = 500
    default_price: float = 0.0
    category_separator: str = "/"


class ProductNormalizer:
    """Handles cleaning and normalization of raw product data."""

    # Brand variations mapping
    BRAND_MAPPINGS = {
        "h&m": ["h&m", "h & m", "h and m", "hm"],
        "oura": ["oura", "oura ring", "oura rings"],
        "whoop": ["whoop", "whoop strap", "whoop band"],
    }

    # Availability status mappings
    AVAILABILITY_MAPPINGS = {
        "in_stock": ["in stock", "instock", "available", "in_stock"],
        "out_of_stock": [
            "out of stock",
            "outofstock",
            "unavailable",
            "not available",
            "out_of_stock",
        ],
    }

    def __init__(self, config: Optional[NormalizationConfig] = None):
        self.config = config or NormalizationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    def normalize(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize a single product record.

        Args:
            product: Raw product dictionary

        Returns:
            Normalized product dictionary
        """
        normalized = product.copy()

        # Normalize each field
        normalized["id"] = self._normalize_id(product)
        normalized["brand"] = self._normalize_brand(product.get("brand", ""))
        normalized["category"] = self._normalize_category(product.get("category", ""))
        normalized["price"] = self._normalize_price(product.get("price"))
        normalized["availability"] = self._normalize_availability(
            product.get("availability", "")
        )
        normalized["image_link"] = self._normalize_image_link(
            product.get("image_urls", "")
        )
        normalized["title"] = self._normalize_text(
            product.get("title", ""), self.config.max_title_length
        )
        normalized["description"] = self._normalize_text(
            product.get("description", ""), self.config.max_description_length
        )

        # dropping image_urls as we have image_link now
        if "image_urls" in normalized:
            del normalized["image_urls"]
            self.logger.info("Dropped 'image_urls' field after normalization.")

        self.logger.info("Normalization complete for product ID: %s", normalized["id"])
        return normalized

    def _normalize_id(self, product: Dict[str, Any]) -> str:
        """Extract and normalize product ID."""
        product_id = product.get("product_id", product.get("id", ""))
        return str(product_id).strip()

    def _normalize_brand(self, brand: str) -> str:
        """Normalize brand names to consistent format."""
        if not brand:
            return ""

        brand_lower = brand.lower().strip()

        # Check brand mappings
        for normalized_brand, variations in self.BRAND_MAPPINGS.items():
            if brand_lower in [v.lower() for v in variations]:
                return normalized_brand.upper()

        return brand.strip().title()

    def _normalize_category(self, category: str) -> str:
        """
        Normalize product category to consistent hierarchical format.

        Examples:
            "clothes>women>dresses" → "clothes/women/dresses"
            "Mens Tops" → "mens/tops"
        """
        if not category:
            return ""

        # Replace various separators with standard separator
        normalized = category.lower().strip()
        normalized = re.sub(
            r"[>,\s]+", self.config.category_separator, normalized
        )  # Replace >, , and whitespace
        normalized = re.sub(
            r"/+", self.config.category_separator, normalized
        )  # Remove duplicate separators

        return normalized.strip(
            self.config.category_separator
        )  # Clean leading/trailing separators

    def _normalize_price(self, price: Any) -> float:
        """Normalize price to float value."""
        if pd.isna(price) or price is None or price == "":
            return self.config.default_price

        if isinstance(price, (int, float)):
            return max(float(price), 0.0)

        # Extract numeric value from string
        price_str = str(price)
        price_match = re.search(r"[\d.]+", price_str)

        if price_match:
            try:
                return max(float(price_match.group()), 0.0)
            except ValueError:
                pass

        return self.config.default_price

    def _normalize_availability(self, availability: str) -> str:
        """Normalize availability status."""
        if not availability:
            return "out_of_stock"  # it depends on context, but safer to assume out of stock

        availability_lower = availability.lower().strip().replace(" ", "")

        # Check availability mappings
        for status, variations in self.AVAILABILITY_MAPPINGS.items():
            if any(var.replace(" ", "") in availability_lower for var in variations):
                return status

        return "out_of_stock"  # Default to out of stock if unclear

    def _normalize_image_link(self, image_urls: str) -> str:
        """Extract primary image link from image URLs."""
        if not image_urls or pd.isna(image_urls):
            return ""

        image_str = str(image_urls).strip()

        # Handle multiple URLs separated by pipe.
        # It depends on context, but here it takes the first valid URL.
        if "|" in image_str:
            image_str = image_str.split("|")[0].strip()

        # URL validation regex
        url_pattern = re.compile(r"^(https?://|www\.)[^\s/$.?#].[^\s]*$", re.IGNORECASE)

        if image_str and url_pattern.match(image_str):
            return image_str

        return ""

    def _normalize_text(self, text: str, max_length: int) -> str:
        """Normalize text fields with length constraints."""
        if not text:
            return ""

        normalized = str(text).strip()

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)

        # Truncate if too long
        if len(normalized) > max_length:
            normalized = normalized[: max_length - 3] + "..."

        return normalized
