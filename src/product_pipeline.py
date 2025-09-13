import json
import re
from typing import Dict, List
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from data_utils import DataLoader
from normalizer import ProductNormalizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProductPipeline:
    """Simple but practical pipeline for AI-ready product data"""

    def __init__(self):
        # A lightweight model for semantic embeddings
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        # Simple but effective intent patterns
        self.intent_map = {
            "affordable": ["cheap", "budget", "value", "affordable", "under"],
            "summer": ["summer", "light", "breathable", "cotton", "warm weather"],
            "eco_friendly": ["organic", "eco", "sustainable", "green"],
            "casual": ["casual", "everyday", "basic", "comfortable", "daily"],
            "comfort": ["comfortable", "soft", "cozy", "warm", "stretch"],
        }
        self.data_loader = DataLoader()
        self.normalizer = ProductNormalizer()

    def normalize_product(self, product: Dict) -> Dict:
        """Clean and normalize product data"""
        return self.normalizer.normalize(product)

    def extract_intents(self, product: Dict) -> List[str]:
        """Extract user intents from product text"""
        text = f"{product.get('title', '')} {product.get('description', '')}".lower()
        intents = []

        # Check for intent patterns
        for intent, keywords in self.intent_map.items():
            if any(kw in text for kw in keywords):
                intents.append(intent)

        # Price-based intent
        if product.get("price", 0) < 30:
            intents.append("budget_friendly")

        # Category-based intents
        category = product.get("category", "")
        if "dress" in category:
            intents.append("dress_shopping")
        elif "hoodie" in category:
            intents.append("cozy_wear")

        return list(set(intents))

    def extract_features(self, product: Dict) -> List[str]:
        """Extract key features from product"""
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

        return features

    def create_ai_optimized_content(self, product: Dict) -> Dict:
        """Generate AI-optimized title and description"""
        brand = product.get("brand", "")
        title = product.get("title", "")
        desc = product.get("description", "")
        intents = product.get("intents", [])
        features = product.get("features", [])

        # Create informative AI title
        audience = (
            "Women"
            if "women" in product.get("category", "")
            else "Men"
            if "men" in product.get("category", "")
            else "Kids"
            if "kids" in product.get("category", "")
            else ""
        )

        # Build optimized title
        ai_title = f"{brand} {audience} {title}".strip()
        if "organic" in features:
            ai_title = f"Eco-Friendly {ai_title}"

        # Build optimized description
        ai_desc = desc
        if intents:
            ai_desc += f". Perfect for {', '.join(intents[:2]).replace('_', ' ')}"
        if features:
            key_features = ", ".join(features[:3]).replace("_", " ")
            ai_desc += f". Features: {key_features}"

        product["ai_optimized_title"] = ai_title[:150]  # Max 150 chars
        product["ai_optimized_description"] = ai_desc[:500]  # Max 500 chars

        return product

    def build_knowledge_graph(self, products: List[Dict]) -> Dict:
        """Create simple knowledge graph representation"""
        graph = {"products": {}, "relationships": []}

        for product in products:
            pid = product["id"]

            # Create product node
            graph["products"][pid] = {
                "title": product.get("ai_optimized_title", product["title"]),
                "category": product.get("category", ""),
                "intents": product.get("intents", []),
                "features": product.get("features", []),
                "price": product.get("price", 0),
            }

            # Create relationships based on shared intents
            for intent in product.get("intents", []):
                graph["relationships"].append(
                    {"type": "serves_intent", "source": pid, "target": intent}
                )

            # Create relationships based on category
            if product.get("category"):
                graph["relationships"].append(
                    {"type": "belongs_to", "source": pid, "target": product["category"]}
                )

        return graph

    def match_query(self, query: str, products: List[Dict]) -> List[Dict]:
        """Match user query to products using embeddings"""
        # Encode query
        query_embedding = self.encoder.encode(query)

        results = []
        for product in products:
            # Create product text for embedding
            product_text = f"{product.get('ai_optimized_title', '')} {product.get('ai_optimized_description', '')}"
            product_embedding = self.encoder.encode(product_text)

            # Calculate similarity
            similarity = np.dot(query_embedding, product_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(product_embedding)
            )

            # Check for direct matches
            query_lower = query.lower()
            boost = 0

            # Price matching
            if "under" in query_lower or "below" in query_lower:
                try:
                    price_limit = float(re.findall(r"\d+", query)[0])
                    if product["price"] <= price_limit:
                        boost += 0.2
                except (ValueError, IndexError):
                    pass

            # Intent matching
            for intent in product.get("intents", []):
                if intent.replace("_", " ") in query_lower:
                    boost += 0.1

            results.append(
                {
                    "product": product,
                    "score": float(similarity) + boost,
                    "match_reason": self._get_match_reason(query, product, similarity),
                }
            )

        # Sort by score and return top matches
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:3]

    def _get_match_reason(self, query: str, product: Dict, similarity: float) -> str:
        """Explain why product matches query"""
        reasons = []

        if similarity > 0.5:
            reasons.append("Strong semantic match")

        query_lower = query.lower()

        # Check price
        if "under" in query_lower and product["price"] < 50:
            reasons.append(f"Price in range (${product['price']})")

        # Check features
        for feature in product.get("features", []):
            if feature.replace("_", " ") in query_lower:
                reasons.append(f"Has {feature.replace('_', ' ')}")

        return ". ".join(reasons) if reasons else "Partial match"

    def process_pipeline(
        self, input_csv: str, schema_json: str, queries_json: str
    ) -> Dict:
        """Run the complete pipeline"""

        # 1. Load data
        products = self.data_loader.load_data(input_csv, "csv")

        schema = self.data_loader.load_data(schema_json, "json")

        queries_data = self.data_loader.load_data(queries_json, "json")
        queries = queries_data.get("queries", [])

        # logger.info(f"Products: {products}")
        # logger.info(f"Schema: {schema}")
        # logger.info(f"Queries: {queries}")

        # 2. Process each product
        enriched_products = []
        for product in products:
            # Normalize
            product = self.normalize_product(product)

            # Extract semantic features
            product["intents"] = self.extract_intents(product)
            product["features"] = self.extract_features(product)

            # Create AI-optimized content
            product = self.create_ai_optimized_content(product)

            enriched_products.append(product)

        # 3. Build knowledge graph (for 3 products as required)
        graph = self.build_knowledge_graph(enriched_products[:3])

        # 4. Test query matching
        query_results = {}
        for query in queries:
            matches = self.match_query(query, enriched_products)
            query_results[query] = [
                {
                    "product_id": m["product"]["id"],
                    "title": m["product"]["ai_optimized_title"],
                    "score": m["score"],
                    "reason": m["match_reason"],
                }
                for m in matches
            ]

        return {
            "enriched_products": enriched_products,
            "knowledge_graph": graph,
            "query_results": query_results,
        }


def main():
    """Main execution"""
    # Setup paths
    data_dir = Path("data")
    input_dir = data_dir / "input"
    output_dir = data_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create sample data if needed
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # Run pipeline
    pipeline = AIProductPipeline()
    results = pipeline.process_pipeline(
        str(input_dir / "raw_products.csv"),
        str(input_dir / "ai_schema.json"),
        str(input_dir / "ai_queries.json"),
    )

    # Save outputs
    with open(output_dir / "enriched_products.json", "w") as f:
        json.dump(results["enriched_products"], f, indent=2)

    with open(output_dir / "knowledge_graph.json", "w") as f:
        json.dump(results["knowledge_graph"], f, indent=2)

    with open(output_dir / "query_results.json", "w") as f:
        json.dump(results["query_results"], f, indent=2)

    logger.info("Pipeline completed successfully!")
    logger.info(f"Results saved to {output_dir}")
    logger.info(f"Processed {len(results['enriched_products'])} products")
    logger.info(f"Matched {len(results['query_results'])} queries")


if __name__ == "__main__":
    main()
