# AI-Ready Product Data Pipeline

This project transforms messy e-commerce product data into AI-ready formats that work well with ChatGPT, Gemini, and other AI platforms.

## What It Does

Takes raw product data like this:
```
"Ladies Dress","summer cotton dress","H & M","clothes>women>dresses",29.99,instock
```

And creates AI-optimized data like this:
```json
{
  "title": "H&M Women Ladies Dress",
  "ai_optimized_content": "H&M Women Ladies Dress. summer cotton dress. Perfect for budget friendly, dress shopping. Features: cotton",
  "intents": ["budget_friendly", "dress_shopping", "fashion", "style", "summer"],
  "features": ["cotton"],
  "relationships": [
    {"type": "serves_intent", "source": "HM001", "target": "summer"}
  ]
}
```

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the pipeline**:
   ```bash
   make run
   ```

3. **Check results** in `data/output/`:
   - `enriched_products.json` - Cleaned and enhanced product data
   - `knowledge_graph.json` - Product relationships and connections  
   - `query_results.json` - Example search results for test queries

## How It Works

### 1. Data Cleaning
- Fixes messy brand names ("H & M" → "H&M")
- Normalizes categories ("clothes>women>dresses" → "clothes/women/dresses")
- Standardizes prices and availability

### 2. Feature Extraction
- Finds materials (cotton, denim, organic)
- Detects styles (slim fit, stretchy)
- Identifies colors (white, blue, black)

### 3. Intent Detection
- Maps products to user needs ("summer outfit", "budget-friendly")
- Uses keywords, categories, and price ranges
- Creates searchable tags for AI systems

### 4. AI Optimization
- Rewrites product titles and descriptions for clarity
- Adds context about target audience and use cases
- Optimizes for LLM queries

### 5. Knowledge Graph
- Connects products to intents and categories
- Shows relationships between similar items (Adjancency matrix)
- Helps AI systems discover related products

### 6. Query Testing
- Tests real user questions like "affordable summer dresses under $30"
- Ranks products by relevance using semantic similarity
- Shows why each product matches the query

## Example Query Results

**Query**: "affordable summer dresses under $30"

**Results**:
1. H&M Women Ladies Dress ($29.99) - Price in range, summer intent
2. Basic T-shirt ($12.99) - Price in range, partial match
3. Kids Jeans ($19.99) - Price in range, partial match

## Project Structure

```
src/
├── main.py                          # entry point
├── product_pipeline.py              # core pipeline logic
└── pipeline_components/
    ├── data_loader.py               # 1. Load CSV/JSON files
    ├── normalizer.py                # 2. Clean messy data
    ├── feature_extractor.py         # 3. Extract product features
    ├── semantic_enricher.py         # 4. Add intents and optimize content
    ├── knowledge_graph.py           # 5. Build product relationships
    ├── query_matcher.py             # 6. Match user queries to products
    └── schema_validator.py          # Validate against AI schema

data/
├── input/
│   ├── raw_products.csv             # Original raw product data
│   ├── ai_schema.json               # Validation rules
│   └── ai_queries.json              # Testset queries
└── output/
    ├── enriched_products.json       # Cleaned and enhanced products
    ├── knowledge_graph.json         # Product relationships
    └── query_results.json           # Search results for test queries
```

## Development

**Add new intent detection**:
Edit `pipeline_components/semantic_enricher.py` and add keywords to `intent_keywords` dictionary.

**Add new features**:
Edit `pipeline_components/feature_extractor.py` and add detection logic to the `extract()` method.

**Test with new queries**:
Add queries to `data/input/ai_queries.json` and run the pipeline.


**Format code**:
I added a basic makefile to check code formatting quality.

```bash
make ruff
```

## Next Steps. Technical Improvements
- Improve pipeline efficiency with parallel processing in case of large datasets.
- Move JSON data to a proper key-value store or graph database.
- Implement a proper REST API for querying.
- Add unit tests for each pipeline component, and e2e tests for the full pipeline.
- More proper logging.
- Orchestrate with Airflow or similar tools.
- DevOps: Containerization and CI/CD for easier and idempotent deployment.
