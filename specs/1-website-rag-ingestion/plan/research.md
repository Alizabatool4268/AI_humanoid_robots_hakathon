# Research Document: Website-based Knowledge Ingestion and Vectorization Pipeline

**Feature**: 1-website-rag-ingestion
**Created**: 2025-12-17
**Status**: Completed

## Decision: Chunk Size Tradeoffs (300-500 words)

### Rationale
The 300-500 word range provides an optimal balance between semantic context and search precision for RAG applications. This range allows each chunk to contain sufficient context for understanding while maintaining specificity for relevant search results.

**Technical Justification:**
- **Lower bound (300 words)**: Provides enough context for semantic understanding and avoids overly granular chunks that might lose meaning
- **Upper bound (500 words)**: Prevents dilution of relevance where multiple topics might be contained in a single chunk
- **Context preservation**: Most paragraphs and sections in documentation sites fall within this range
- **Search performance**: Optimal for vector similarity calculations without being too computationally expensive

### Alternatives Considered
1. **Fixed 200-word chunks**: Risk of breaking semantic context and losing meaning
2. **Fixed 800-word chunks**: Potential for reduced precision due to topic mixing
3. **Sentence-based chunks**: Complex to implement and may result in inconsistent semantic boundaries
4. **Header-based chunks**: Dependent on document structure, may result in very large or very small chunks

### Decision Outcome
300-500 word chunks with boundary respect for sentences and semantic sections.

## Decision: Cohere vs Other Embedding Providers

### Rationale
Cohere's embed-english-v3.0 model was selected based on performance benchmarks, API reliability, and feature set for English text content typical of documentation websites.

**Technical Justification:**
- **Performance**: State-of-the-art results for English text similarity tasks
- **API Reliability**: Consistent response times and uptime
- **Documentation**: Well-documented API with good Python SDK
- **Cost-effectiveness**: Competitive pricing for the expected volume
- **Model consistency**: Ensures same model used for both ingestion and future query embeddings

### Alternatives Considered
1. **OpenAI embeddings**: Good quality but different API patterns, potentially higher cost
2. **Hugging Face models**: Self-hosted options available but require infrastructure management
3. **Sentence Transformers**: Open source but may be slower than managed APIs
4. **Google embeddings**: Good alternative but Cohere showed better performance on documentation text

### Decision Outcome
Use Cohere embed-english-v3.0 for both ingestion and future query embeddings to ensure consistency.

## Decision: Qdrant Vector DB vs Relational Storage

### Rationale
Qdrant is purpose-built for vector similarity search with optimized cosine similarity operations, making it superior to relational databases for semantic search use cases.

**Technical Justification:**
- **Vector optimization**: Specifically designed for high-dimensional vector storage and search
- **Cosine similarity**: Native support for cosine similarity calculations
- **Scalability**: Efficient indexing for vector search operations
- **Performance**: Optimized for the nearest neighbor search required for semantic similarity
- **API**: Clean Python client with batch operations support

### Alternatives Considered
1. **PostgreSQL with pgvector**: Good option but Qdrant is optimized specifically for this use case
2. **Elasticsearch**: Capable of vector search but more complex setup for pure vector use case
3. **Pinecone**: Managed service alternative but Qdrant offers more control and open source option
4. **Milvus**: Competitor to Qdrant but Qdrant has simpler setup for this use case

### Decision Outcome
Use Qdrant with cosine similarity for optimal vector search performance.

## Decision: Website Ingestion vs Local File Ingestion

### Rationale
Direct website ingestion ensures the most up-to-date content and matches the requirement to crawl the live ai-humanoid-robots-hakathon.vercel.app website.

**Technical Justification:**
- **Freshness**: Always uses the latest content from the live site
- **Automation**: Can be run periodically to update the knowledge base
- **Efficiency**: No manual export/import steps required
- **Completeness**: Captures all content as presented on the live site

### Alternatives Considered
1. **Local markdown files**: Would require manual export process and potential formatting loss
2. **Static HTML export**: Additional preprocessing step with potential content degradation
3. **API-based extraction**: Not available for static Docusaurus sites
4. **Git repository content**: Only works if content is in version control

### Decision Outcome
Implement direct website crawling from ai-humanoid-robots-hakathon.vercel.app using sitemap.xml for URL discovery.

## Best Practices: Web Crawling

### Identified Best Practices
1. **Respect robots.txt**: Always check and follow robots.txt rules
2. **Rate limiting**: Implement appropriate delays between requests to avoid overwhelming the server
3. **User-Agent identification**: Use descriptive user-agent string
4. **Error handling**: Robust handling of network errors, timeouts, and invalid responses
5. **Domain restriction**: Only crawl URLs within the specified domain
6. **Sitemap utilization**: Use sitemap.xml for efficient URL discovery

### Technical Implementation Notes
- Use `requests` library with appropriate headers and timeout settings
- Implement exponential backoff for retry logic
- Include proper error logging for debugging
- Validate URLs before processing to ensure they're within scope

## Best Practices: Content Extraction

### Identified Best Practices
1. **Semantic HTML parsing**: Use proper HTML parsing libraries (BeautifulSoup) rather than regex
2. **Selective extraction**: Focus on content tags (h1-h6, p, li, blockquote) while excluding navigation
3. **Metadata preservation**: Capture title, headings hierarchy, and page context
4. **Text cleaning**: Remove extra whitespace, special characters, and HTML artifacts
5. **Encoding handling**: Properly handle character encodings to avoid corruption

### Technical Implementation Notes
- Use CSS selectors to target content areas specifically
- Implement fallbacks for different HTML structures
- Preserve document hierarchy in metadata
- Handle various content formats (text, lists, code blocks)

## Best Practices: Text Chunking

### Identified Best Practices
1. **Boundary respect**: Maintain sentence boundaries and avoid breaking mid-sentence
2. **Semantic awareness**: Respect section/heading boundaries when possible
3. **Size consistency**: Maintain target size range while respecting content structure
4. **Metadata retention**: Preserve source information with each chunk
5. **Overlap handling**: Consider minimal overlap for better context recovery (optional)

### Technical Implementation Notes
- Use word counting rather than character counting for more consistent semantic size
- Implement look-ahead to find appropriate break points
- Validate chunk size compliance with min/max bounds
- Include chunk positioning information for potential reassembly

## Best Practices: Embedding Generation

### Identified Best Practices
1. **Batch processing**: Process multiple chunks together for API efficiency
2. **Rate limiting**: Respect API rate limits and implement appropriate delays
3. **Error handling**: Handle API failures and retry logic appropriately
4. **Consistency**: Use same model and parameters for ingestion and query time
5. **Cost management**: Monitor API usage and optimize batch sizes

### Technical Implementation Notes
- Implement batch processing with optimal batch size for Cohere API
- Include proper authentication and error handling
- Cache embeddings if needed for development/testing
- Validate embedding dimensions match expected size

## Best Practices: Vector Storage

### Identified Best Practices
1. **Collection design**: Properly configure collection with appropriate vector dimensions
2. **Metadata schema**: Store all required metadata in payload for retrieval
3. **Indexing**: Ensure proper indexing for efficient similarity search
4. **Data validation**: Validate data format before storage
5. **Connection management**: Proper client lifecycle management

### Technical Implementation Notes
- Set up Qdrant collection with cosine similarity metric
- Use proper payload schema matching the requirements
- Implement batch storage operations for efficiency
- Include proper error handling and retry logic