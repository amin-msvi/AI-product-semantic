from typing import Dict, List
import logging


class ContentOptimizer:
    """Optimizes product content for AI platforms."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_title_length = 150
        self.max_description_length = 500
    
    def optimize_content(self, product: Dict) -> Dict:
        """Create AI-optimized title and description."""

        product["ai_optimized_title"] = self._create_optimized_title(product)
        product["ai_optimized_description"] = self._create_optimized_description(product)
        
        self.logger.info(f"Optimized content for product {product.get('id', 'N/A')}")
        
        return product
    
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
            optimized_title = optimized_title[:self.max_title_length - 3] + "..."
            
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
            optimized_desc = optimized_desc[:self.max_description_length - 3] + "..."
            
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
