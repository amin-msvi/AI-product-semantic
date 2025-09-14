# Architecture Decision Record (ADR)
## AI-Ready Product Data Pipeline

### Problem
Most product catalogs are built for regular e-commerce websites, but AI platforms like ChatGPT and Gemini need different data formats to recommend products when people ask questions in natural language.

I want to build a pipeline that takes messy product data and transforms it into something AI systems can easily understand and search through.

### Solution Overview
I built a pipeline with 5 main steps:
1. **Clean the raw data** - Fix brand names, categories, prices, and availability
2. **Extract features** - Find important product details like materials and colors
3. **Add semantic meaning** - Figure out what people might want this product for and add an AI optimized description for LLMs.
4. **Knowledge graph** - Create a knowledge graph showing how products relate to each other
5. **Test with real queries** - Make sure the system can find the right products when people ask questions

### Key Technical Decisions

#### 1. Semantic Enrichment Strategy  
**Decision**: Use keyword-based intent mapping + AI-optimized content field.
**Why**: Simple and fast approach that works well for the prototype. I extract user intents like "budget-friendly" or "summer outfit" from product text and prices, then rewrite descriptions to be clearer for AI systems.

#### 2. Knowledge Graph Structure
**Decision**: Simple node-relationship format with products as nodes and intents/categories as connections.
**Why**: Easy for AI systems to understand product relationships. For example, a dress connects to "summer outfit" intent and "women's clothing" category.

#### 3. Query Matching Approach
**Decision**: Combine semantic similarity (using a lightweight sentence transformer) with rule-based boosts.
**Why**: 
- Semantic similarity catches the meaning of queries
- Rule-based boosts handle hard constraints like price ranges ("under $30")
- This hybrid approach makes a balance between fuzzy and hard constraints.

#### 5. Data Processing Pipeline
**Decision**: Linear and simple pipeline with modular components.
**Why**: Making it easy to test, debug, and improve individual parts.

### How This Scales for AI Platforms

**AI Platform Benefits**:
- Feature extraction and intent mapping connect products to real user needs.
- AI-optimized content and semantic intents make products easier to find and match user questions.
- Knowledge graph shows related products.
- Similarity scoring ranks the best matches for queries.

### Trade-offs Made

**Simplicity vs. Sophistication**: 
- Chose keyword-based intent extraction over complex ML models because of the following reasons:
  - Time limits (48h) to implement
  - Lack of large datasets for training
  - Prototype focus
- Faster to build and easier to understand.

**Speed vs. Accuracy**:
- Used lightweight semantic model (MiniLM) instead of larger and more accurate models in order to be able to run on a local machine.
- Good balance for prototype - fast enough to demo, accurate enough to be meaningful.

**Coverage vs. Precision**:
- Added scores in order to quantify how well products match queries.
- Built context-based rules for common cases (price, materials, basic intents)
- It works well for the existing product categories for demo purposes. I added one example to raw-data to test some normalization and enrichment.

### Future Improvements

1. **Better Intent Detection**: Use ML models trained on product-query pairs (data collection needed)
2. **Dynamic Feature Extraction**: Automatically discover new product features from descriptions. Also, Image2Vec for visual features would be great.
3. **Multi-category Support**: Expand beyond clothing to wellness (e.g., whoop, oura), electronics (e.g., smart home devices), home goods (e.g., furniture, kitchenware), etc.
4. **Real-time Updates**: Handle product availability and price changes (event-driven architecture)
5. **A/B Testing**: Measure which optimizations actually improve AI discoverability (CTR, conversion)
6. **Attribution**: Track impressions and clicks from AI platforms back to products.

### Success Metrics
- Products are findable by AI when users ask natural questions
- Search results match user intent (right product type, price range, features)
- Knowledge graph helps discover related products
- Pipeline processes new products quickly and accurately
