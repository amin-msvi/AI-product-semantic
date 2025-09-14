from typing import Dict
import logging


class SemanticEnricher:
    """Extracts user intents and optimizes content for AI platforms."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_title_length = 150
        self.max_description_length = 500

        # Simple keyword-based intent mapping
        self.intent_keywords = {
            "affordable": ["cheap", "budget", "value", "affordable", "under"],
            "summer": ["summer", "light", "breathable", "cotton", "warm weather"],
            "eco_friendly": ["organic", "eco", "sustainable", "green"],
            "casual": ["casual", "everyday", "basic", "comfortable", "daily"],
            "comfort": ["comfortable", "soft", "cozy", "warm", "stretch"],
        }

        self.category_keywords = {
            "dress": ["dress_shopping", "fashion", "style"],
            "hoodie": ["cozy_wear", "casual_wear"],
            "sneaker": ["footwear", "active_wear"],
            "jacket": ["outerwear", "cold_weather"],
            "t-shirt": ["casual_wear", "everyday_wear"],
        }

        # Price-based thresholds
        self.budget_threshold = 30.0

    def enrich_content(self, product: Dict) -> Dict:
        """Extract intents and create optimized content."""
        # Extract user intents
        product["intents"] = self._extract_intents(product)
        
        # Create optimized content
        product["ai_optimized_content"] = self._create_optimized_content(product)

        self.logger.info(f"Optimized content for product {product.get('id', 'N/A')}")
        return product

    def _extract_intents(self, product):
        """Extract user intents from product data."""
        intents = set()

        # Text-based intent extraction
        text = f"{product.get('title', '')} {product.get('description', '')}".lower()
        intents.update(self._extract_text_intents(text))

        # Price-based intents
        intents.update(self._extract_price_intents(product.get("price", 0)))

        # Category-based intents
        intents.update(self._extract_category_intents(product.get("category", "")))

        result = sorted(list(intents))
        self.logger.info(
            f"Extracted {len(result)} intents for product {product.get('id', 'N/A')}"
        )

        return result

    def _extract_text_intents(self, text):
        """Extract intents from product text."""
        intents = set()

        for intent, keywords in self.intent_keywords.items():
            if any(keyword in text for keyword in keywords):
                intents.add(intent)

        return intents

    def _extract_price_intents(self, price):
        """Extract price-based intents."""
        intents = set()

        if 0 < price < self.budget_threshold:
            intents.add("budget_friendly")

        return intents

    def _extract_category_intents(self, category):
        """Extract category-based intents."""
        intents = set()
        category_lower = category.lower()

        for keyword, mapped_intents in self.category_keywords.items():
            if keyword in category_lower:
                intents.update(mapped_intents)

        return intents

    def _create_optimized_content(self, product: Dict) -> str:
        """Create single optimized content combining title and description."""
        # Create optimized title
        optimized_title = self._create_optimized_title(product)
        
        # Create optimized description
        optimized_description = self._create_optimized_description(product)
        
        # Combine them into single content
        combined_content = f"{optimized_title}. {optimized_description}".strip()
        
        return combined_content

    def _create_optimized_title(self, product: Dict) -> str:
        """Create AI-optimized product title."""
        components = []

        # Add eco-friendly prefix if applicable
        if "organic" in product.get("features", []):
            components.append("Eco-Friendly")

        # Add brand
        brand = product.get("brand", "")
        if brand:
            components.append(brand)

        # Add audience from category
        audience = self._extract_audience(product.get("category", ""))
        if audience:
            components.append(audience)

        # Add original title
        title = product.get("title", "")
        if title:
            components.append(title)

        # Join and truncate
        optimized_title = " ".join(components).strip()

        if len(optimized_title) > self.max_title_length:
            optimized_title = optimized_title[: self.max_title_length - 3] + "..."

        return optimized_title

    def _create_optimized_description(self, product: Dict) -> str:
        """Create AI-optimized product description."""
        components = []

        # Starting with original description
        original_desc = product.get("description", "")
        if original_desc:
            components.append(original_desc)

        # Adding intent information
        intents = product.get("intents", [])
        if intents:
            # Take first 2 intents and make them readable
            readable_intents = [intent.replace("_", " ") for intent in intents[:2]]
            components.append(f"Perfect for {', '.join(readable_intents)}")

        # Adding feature information
        features = product.get("features", [])
        if features:
            # Take first 3 features and make them readable
            readable_features = [feature.replace("_", " ") for feature in features[:3]]
            components.append(f"Features: {', '.join(readable_features)}")

        # Join and truncate
        optimized_desc = ". ".join(components).strip()

        if len(optimized_desc) > self.max_description_length:
            optimized_desc = optimized_desc[: self.max_description_length - 3] + "..."

        return optimized_desc

    def _extract_audience(self, category: str) -> str:
        """Extract target audience from product category."""
        category_lower = category.lower()

        if "women" in category_lower:
            return "Women"
        elif "men" in category_lower:
            return "Men"
        elif "kids" in category_lower:
            return "Kids"

        return ""
