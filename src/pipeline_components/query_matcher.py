import re
import numpy as np
from sentence_transformers import SentenceTransformer
import logging


class QueryMatcher:
    """Matches user queries to products using semantic similarity."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Lightweight semantic encoder
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.top_results = 3

    def match_query(self, query, products):
        """Match a user query to relevant products."""
        if not products:
            return []

        # Encode the query
        query_embedding = self.encoder.encode(query)

        results = []

        for product in products:
            # Calculate semantic similarity
            similarity_score = self._calculate_similarity(query_embedding, product)

            # Calculate boost score from direct matches
            boost_score = self._calculate_boost_score(query, product)

            # Combine scores
            final_score = similarity_score + boost_score

            # Generate match reason
            match_reason = self._generate_match_reason(query, product, similarity_score)

            results.append(
                {
                    "product_id": product.get("id", ""),
                    "description": product.get("ai_optimized_content", product.get("title", "")),
                    "score": float(final_score),
                    "reason": match_reason,
                }
            )

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)

        self.logger.info(f"Matched query '{query}' to {len(results)} products")

        return results[: self.top_results]

    def _calculate_similarity(self, query_embedding, product):
        """Calculate semantic similarity between query and product."""
        # Create product text for embedding
        product_text = self._create_product_text(product)

        if not product_text.strip():
            return 0.0

        # Encode product text
        product_embedding = self.encoder.encode(product_text)

        # Calculate cosine similarity
        similarity = np.dot(query_embedding, product_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(product_embedding)
        )

        return float(similarity)

    def _calculate_boost_score(self, query, product):
        """Calculate boost score from direct matches."""
        query_lower = query.lower()
        boost = 0.0

        # Price matching boost
        boost += self._get_price_boost(query_lower, product)

        # Intent matching boost
        boost += self._get_intent_boost(query_lower, product)

        # Feature matching boost
        boost += self._get_feature_boost(query_lower, product)

        return boost

    def _get_price_boost(self, query_lower, product):
        """Calculate price-based boost score."""
        if "under" not in query_lower and "below" not in query_lower:
            return 0.0

        try:
            # Extract price limit from query
            price_matches = re.findall(r"\d+", query_lower)
            if not price_matches:
                return 0.0

            price_limit = float(price_matches[0])
            product_price = product.get("price", 0)

            if product_price <= price_limit:
                return 0.2  # Significant boost for price match

        except (ValueError, IndexError):
            pass

        return 0.0

    def _get_intent_boost(self, query_lower, product):
        """Calculate intent-based boost score."""
        boost = 0.0

        for intent in product.get("intents", []):
            intent_readable = intent.replace("_", " ")
            if intent_readable in query_lower:
                boost += 0.1

        return boost

    def _get_feature_boost(self, query_lower, product):
        """Calculate feature-based boost score."""
        boost = 0.0

        for feature in product.get("features", []):
            feature_readable = feature.replace("_", " ")
            if feature_readable in query_lower:
                boost += 0.05

        return boost

    def _create_product_text(self, product):
        """Create searchable text representation of product."""
        components = [
            product.get("ai_optimized_content", ""),
            " ".join(product.get("intents", [])),
            " ".join(product.get("features", [])),
        ]

        return " ".join(filter(None, components))

    def _generate_match_reason(self, query, product, similarity):
        """Generate explanation for why product matches query."""
        reasons = []
        query_lower = query.lower()

        # Semantic similarity reason
        if similarity > 0.5:
            reasons.append("Strong semantic match")

        # Price reason
        if "under" in query_lower and product.get("price", 0) < 50:
            reasons.append(f"Price in range (${product.get('price', 0)})")

        # Feature reasons
        for feature in product.get("features", []):
            feature_readable = feature.replace("_", " ")
            if feature_readable in query_lower:
                reasons.append(f"Has {feature_readable}")

        return ". ".join(reasons) if reasons else "Partial match"
