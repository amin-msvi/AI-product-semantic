import logging


class IntentMapper:
    """Maps product attributes to user intents for AI discovery."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # Simple keyword-based intent mapping
        self.intent_keywords = {
            "affordable": ["cheap", "budget", "value", "affordable", "under"],
            "summer": ["summer", "light", "breathable", "cotton", "warm weather"],
            "eco_friendly": ["organic", "eco", "sustainable", "green"],
            "casual": ["casual", "everyday", "basic", "comfortable", "daily"],
            "comfort": ["comfortable", "soft", "cozy", "warm", "stretch"],
        }

        # Price-based thresholds
        self.budget_threshold = 30.0

    def extract_intents(self, product):
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

        if price > 0 and price < self.budget_threshold:
            intents.add("budget_friendly")

        return intents

    def _extract_category_intents(self, category):
        """Extract category-based intents."""
        intents = set()
        category_lower = category.lower()

        if "dress" in category_lower:
            intents.add("dress_shopping")
        elif "hoodie" in category_lower:
            intents.add("cozy_wear")

        return intents
