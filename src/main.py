import logging
from pathlib import Path
from product_pipeline import AIProductPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    # Setup paths
    data_dir = Path("data")
    input_dir = data_dir / "input"
    output_dir = data_dir / "output"

    # Validate input directory exists
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # Initialize and run pipeline
    pipeline = AIProductPipeline()

    try:
        # Run the complete pipeline
        results = pipeline.process_pipeline(
            input_csv=str(input_dir / "raw_products.csv"),
            schema_json=str(input_dir / "ai_schema.json"),
            queries_json=str(input_dir / "ai_queries.json"),
        )

        # Save all results
        pipeline.save_results(results, str(output_dir))

        # Print summary
        logger.info("=" * 50)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Processed {len(results['enriched_products'])} products")
        logger.info(
            f"Built knowledge graph with {len(results['knowledge_graph']['products'])} nodes"
        )
        logger.info(f"Tested {len(results['query_results'])} search queries")
        logger.info(f"Results saved to: {output_dir}")
        logger.info("=" * 50)

        # Show a sample query result
        if results["query_results"]:
            sample_query = list(results["query_results"].keys())[0]
            sample_results = results["query_results"][sample_query][
                :2
            ]  # First 2 results

            logger.info(f"Sample Query: '{sample_query}'")
            for i, result in enumerate(sample_results, 1):
                logger.info(f"  {i}. {result['title']} (Score: {result['score']:.3f})")
                logger.info(f"     Reason: {result['reason']}")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
