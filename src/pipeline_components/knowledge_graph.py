from typing import Dict, List
import logging


class KnowledgeGraphBuilder:
    """Builds knowledge graph representations for AI platforms."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def build_graph(self, products: List[Dict]) -> Dict:
        """Build knowledge graph from enriched products."""
        graph = {
            "products": {},
            "relationships": []
        }
        
        # Create product nodes
        for product in products:
            product_id = product.get("id", "")
            if not product_id:
                continue
                
            graph["products"][product_id] = self._create_product_node(product)
            
            # Create relationships
            graph["relationships"].extend(self._create_relationships(product))
        
        self.logger.info(f"Built knowledge graph with {len(graph['products'])} products "
                        f"and {len(graph['relationships'])} relationships")
        
        return graph
    
    def _create_product_node(self, product: Dict) -> Dict:
        """Create a product node for the knowledge graph."""
        return {
            "title": product.get("ai_optimized_title", product.get("title", "")),
            "category": product.get("category", ""),
            "intents": product.get("intents", []),
            "features": product.get("features", []),
            "price": product.get("price", 0.0)
        }
    
    def _create_relationships(self, product: Dict) -> List[Dict]:
        """Create relationships for a single product."""
        relationships = []
        product_id = product.get("id", "")
        
        if not product_id:
            return relationships
        
        # Intent relationships
        for intent in product.get("intents", []):
            relationships.append({
                "type": "serves_intent",
                "source": product_id,
                "target": intent
            })
        
        # Category relationships
        category = product.get("category", "")
        if category:
            relationships.append({
                "type": "belongs_to",
                "source": product_id,
                "target": category
            })
        return relationships
