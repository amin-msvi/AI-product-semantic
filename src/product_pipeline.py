from typing import Dict, List
from pathlib import Path
import logging

from pipeline_components.data_loader import DataLoader
from pipeline_components.normalizer import ProductNormalizer
from pipeline_components.feature_extractor import FeatureExtractor
from pipeline_components.intent_mapper import IntentMapper
from pipeline_components.content_optimizer import ContentOptimizer
from pipeline_components.knowledge_graph import KnowledgeGraphBuilder
from pipeline_components.query_matcher import QueryMatcher
from pipeline_components.schema_validator import SchemaValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProductPipeline:
    """Simple but practical pipeline for AI-ready product data"""

    def __init__(self):
        """Initialize all pipeline components."""
        self.data_loader = DataLoader()
        self.normalizer = ProductNormalizer()
        self.feature_extractor = FeatureExtractor()
        self.intent_mapper = IntentMapper()
        self.content_optimizer = ContentOptimizer()
        self.graph_builder = KnowledgeGraphBuilder()
        self.query_matcher = QueryMatcher()
        self.schema_validator = SchemaValidator()
        
        logger.info("AI Product Pipeline initialized")
    
    def process_pipeline(self, input_csv: str, schema_json: str, queries_json: str) -> Dict:
        """
        Run the complete pipeline from raw data to AI-ready outputs.
        
        Args:
            input_csv: Path to raw product CSV file
            schema_json: Path to AI schema JSON file  
            queries_json: Path to test queries JSON file
            
        Returns:
            dict containing all pipeline outputs
        """
        logger.info("Starting AI Product Pipeline")
        
        # Step 1: Load all input data
        products = self._load_input_data(input_csv, schema_json, queries_json)
        raw_products = products['raw_products']
        schema = products['schema']
        queries = products['queries']
        
        # Step 2: Process each product through the enrichment pipeline
        enriched_products = self._enrich_products(raw_products)
        
        # Step 3: Validate enriched products against schema
        self._validate_products(enriched_products, schema)
        
        # Step 4: Build knowledge graph (first 3 products as specified)
        knowledge_graph = self._build_knowledge_graph(enriched_products[:3])
        
        # Step 5: Test query matching
        query_results = self._test_queries(queries, enriched_products)
        
        # Step 6: Prepare final results
        results = {
            "enriched_products": enriched_products,
            "knowledge_graph": knowledge_graph,
            "query_results": query_results
        }
        
        logger.info("Pipeline completed successfully!")
        return results
    
    def _load_input_data(self, input_csv: str, schema_json: str, queries_json: str) -> Dict:
        """Load and validate all input data files."""
        logger.info("Loading input data...")
        
        return {
            "raw_products": self.data_loader.load_data(input_csv, "csv"),
            "schema": self.data_loader.load_data(schema_json, "json"),
            "queries": self.data_loader.load_data(queries_json, "json").get("queries", [])
        }
    
    def _enrich_products(self, raw_products: List[Dict]) -> List[Dict]:
        """Enrich each product with AI-ready semantic data."""
        logger.info(f"Enriching {len(raw_products)} products...")
        
        enriched_products = []
        
        for product in raw_products:
            # Step 1: Normalize messy data
            product = self.normalizer.normalize(product)
            
            # Step 2: Extract semantic features
            product["features"] = self.feature_extractor.extract(product)
            
            # Step 3: Map to user intents
            product["intents"] = self.intent_mapper.extract_intents(product)
            
            # Step 4: Optimize content for AI platforms
            product = self.content_optimizer.optimize_content(product)
            
            enriched_products.append(product)
        
        logger.info(f"Successfully enriched {len(enriched_products)} products")
        return enriched_products
    
    def _validate_products(self, products: List[Dict], schema: Dict) -> None:
        """Validate all products against the AI schema."""
        logger.info("Validating products against schema...")
        
        validation_results = self.schema_validator.validate_batch(products, schema)
        
        if validation_results:
            summary = self.schema_validator.get_validation_summary(validation_results)
            logger.warning(f"Schema validation issues found:\n{summary}")
        else:
            logger.info("All products passed schema validation")
    
    def _build_knowledge_graph(self, products: List[Dict]) -> Dict:
        """Build knowledge graph representation."""
        logger.info(f"Building knowledge graph for {len(products)} products...")
        
        return self.graph_builder.build_graph(products)
    
    def _test_queries(self, queries: List[str], products: List[Dict]) -> Dict:
        """Test query matching against enriched products."""
        logger.info(f"Testing {len(queries)} queries against products...")
        
        query_results = {}
        
        for query in queries:
            matches = self.query_matcher.match_query(query, products)
            query_results[query] = matches
        
        return query_results
    
    def save_results(self, results: Dict, output_dir: str) -> None:
        """Save all pipeline results to output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save enriched products
        self.data_loader.save_json(
            results["enriched_products"],
            output_path / "enriched_products.json"
        )
        
        # Save knowledge graph
        self.data_loader.save_json(
            results["knowledge_graph"],
            output_path / "knowledge_graph.json"
        )
        
        # Save query results
        self.data_loader.save_json(
            results["query_results"],
            output_path / "query_results.json"
        )
        
        logger.info(f"Results saved to {output_path}")
