# Implementation Plan: Website-based Knowledge Ingestion and Vectorization Pipeline

**Feature**: 1-website-rag-ingestion
**Created**: 2025-12-17
**Status**: Draft
**Plan Version**: 1.0

## Technical Context

The implementation will create a Python-based RAG pipeline that ingests content from the ai-humanoid-robots-hakathon.vercel.app website, generates embeddings using Cohere, and stores them in Qdrant. The system will be built in a separate `backend/` directory using `uv` as the package manager.

**Architecture Components:**
- **Ingestion Layer**: Web crawler and content extractor
- **Processing Layer**: Text chunking and metadata preservation
- **Embedding Layer**: Cohere API integration
- **Storage Layer**: Qdrant vector database

**Technology Stack:**
- **Language**: Python 3.10+
- **Package Manager**: uv
- **Web Crawling**: requests, BeautifulSoup, or similar
- **Text Processing**: Natural language processing libraries
- **Embeddings**: Cohere API (embed-english-v3.0)
- **Vector DB**: Qdrant (local or cloud)

**System Dependencies:**
- **Cohere API Key**: For embedding generation
- **Qdrant Instance**: Local Docker or cloud service
- **Python Environment**: Managed by uv

## Architecture Overview

```
[Website URL] → [Sitemap Crawler] → [Content Extractor] → [Text Chunker] → [Cohere Embedder] → [Qdrant Storage]
     ↓              ↓                    ↓                   ↓                  ↓                   ↓
  Source        URL Discovery      Text Cleaning       Chunking          Embedding           Vector DB
  Pages         All Pages          HTML → Text        300-500 words    Vector Generation    book_content
                                                                                             Collection
```

### Data Flow
1. **Crawling**: Use sitemap.xml to discover all accessible pages
2. **Extraction**: Parse HTML to extract meaningful content (headings, paragraphs, lists)
3. **Processing**: Clean and chunk text while preserving metadata
4. **Embedding**: Generate vectors using Cohere's embed-english-v3.0 model
5. **Storage**: Save vectors with metadata to Qdrant collection

## Project Structure

```
backend/
├── pyproject.toml          # Project configuration and dependencies
├── main.py                 # Main pipeline execution
├── requirements-dev.txt    # Development dependencies
├── .env                    # Environment variables (not committed)
├── .gitignore              # Git ignore rules
├── docs/
│   └── setup.md           # Setup and usage documentation
├── src/
│   ├── __init__.py
│   ├── crawler.py         # Website crawling and URL discovery
│   ├── extractor.py       # Content extraction from HTML
│   ├── chunker.py         # Text chunking logic
│   ├── embedder.py        # Cohere API integration
│   └── storage.py         # Qdrant storage operations
├── tests/
│   ├── __init__.py
│   ├── test_crawler.py
│   ├── test_extractor.py
│   ├── test_chunker.py
│   ├── test_embedder.py
│   └── test_storage.py
└── config/
    └── settings.py        # Configuration management
```

## Phase 0: Research & Preparation

### Research Tasks

#### Decision: Chunk Size Tradeoffs
**Rationale**: 300-500 words provides optimal balance between semantic context and search precision. Smaller chunks may lose context, while larger chunks may dilute relevance.

**Alternatives Considered**:
- Fixed 200-word chunks: Too small, loses context
- Fixed 800-word chunks: Too large, reduces precision
- Semantic boundary chunks: Complex to implement, 300-500 range still optimal

#### Decision: Cohere vs Other Embedding Providers
**Rationale**: Cohere's embed-english-v3.0 offers state-of-the-art embeddings with good performance for English text content. Well-documented API and reliable service.

**Alternatives Considered**:
- OpenAI embeddings: Good but requires different API key management
- Hugging Face models: Self-hosted option but requires more infrastructure
- Sentence Transformers: Open source but may be slower than API services

#### Decision: Qdrant Vector DB vs Relational Storage
**Rationale**: Qdrant is purpose-built for vector similarity search with efficient cosine similarity operations. Better performance than relational DBs for semantic search.

**Alternatives Considered**:
- PostgreSQL with pgvector: Good but Qdrant optimized for this use case
- Elasticsearch: Capable but overkill for pure vector search
- Pinecone: Managed service but Qdrant offers more control

#### Decision: Website Ingestion vs Local Markdown Ingestion
**Rationale**: Website ingestion directly from live content ensures most up-to-date information and matches the requirement to crawl ai-humanoid-robots-hakathon.vercel.app.

**Alternatives Considered**:
- Local markdown files: Would require manual export process
- Static HTML export: Additional step, website crawling is more direct

## Phase 1: Design & Contracts

### Data Model

#### Text Chunk Entity
- **id**: Unique identifier (UUID)
- **content**: Text content (300-500 words)
- **url**: Source page URL
- **title**: Page title
- **section**: Section/heading hierarchy
- **word_count**: Number of words in chunk
- **created_at**: Timestamp of creation

#### Vector Embedding Entity
- **chunk_id**: Reference to Text Chunk ID
- **vector**: Array of float values (Cohere embedding)
- **embedding_model**: Model identifier (embed-english-v3.0)
- **embedding_version**: Version of the embedding

#### Metadata Entity
- **chunk_id**: Reference to Text Chunk ID
- **source_url**: Original page URL
- **page_title**: HTML title of source page
- **section_hierarchy**: Breadcrumb path or heading structure
- **crawl_timestamp**: When the page was crawled

### API Contracts (Internal)

#### Crawler Interface
```
get_all_urls(base_url: str, sitemap_url: str) -> List[str]
- Input: Base website URL and sitemap URL
- Output: List of all discoverable page URLs
- Error: Network issues, invalid sitemap
```

#### Extractor Interface
```
extract_text_from_url(url: str) -> Dict[str, Any]
- Input: Page URL
- Output: {"title": str, "content": str, "section_hierarchy": List[str]}
- Error: Invalid URL, network issues, parsing errors
```

#### Chunker Interface
```
chunk_text(text: str, url: str, title: str, section: str) -> List[Dict]
- Input: Raw text, source metadata
- Output: List of chunk dictionaries with content and metadata
- Error: Invalid text input
```

#### Embedder Interface
```
embed(chunks: List[Dict]) -> List[Dict]
- Input: List of text chunks with metadata
- Output: List of chunks with added embedding vectors
- Error: API rate limits, invalid API key
```

#### Storage Interface
```
create_collection(collection_name: str) -> bool
- Input: Collection name
- Output: Success status
- Error: Database connection issues

save_chunk_to_qdrant(chunk: Dict) -> bool
- Input: Chunk with embedding and metadata
- Output: Success status
- Error: Database connection issues, invalid format
```

### Configuration Requirements

#### Environment Variables
- `COHERE_API_KEY`: API key for Cohere service
- `QDRANT_URL`: URL for Qdrant instance (optional, defaults to local)
- `QDRANT_API_KEY`: API key for Qdrant (if using cloud)
- `WEBSITE_URL`: Base URL to crawl (default: ai-humanoid-robots-hakathon.vercel.app)
- `SITEMAP_URL`: Sitemap URL (default: ai-humanoid-robots-hakathon.vercel.app/sitemap.xml)

#### Settings Configuration
- Chunk size range (min: 300, max: 500 words)
- Cohere model name (default: embed-english-v3.0)
- Qdrant collection name (default: book_content)
- Batch processing size for embeddings
- Rate limiting for API calls

## Phase 2: Implementation Plan

### Module 1: Crawler (`src/crawler.py`)
- Implement sitemap parsing to discover all URLs
- Handle robots.txt compliance and rate limiting
- Validate URLs are within the specified domain
- Return list of accessible page URLs

### Module 2: Extractor (`src/extractor.py`)
- Parse HTML content using BeautifulSoup or similar
- Extract headings, paragraphs, and lists while excluding navigation
- Preserve page title and section hierarchy
- Clean HTML tags and return plain text

### Module 3: Chunker (`src/chunker.py`)
- Split text into 300-500 word chunks
- Respect sentence boundaries and section breaks
- Maintain metadata association with chunks
- Validate chunk size compliance

### Module 4: Embedder (`src/embedder.py`)
- Integrate with Cohere API using embed-english-v3.0
- Handle API rate limits and error responses
- Batch process chunks for efficiency
- Validate embedding dimensions

### Module 5: Storage (`src/storage.py`)
- Initialize Qdrant client connection
- Create "book_content" collection with proper configuration
- Store embeddings with metadata payload
- Implement error handling for storage operations

### Main Pipeline (`main.py`)
- Execute pipeline: crawl → extract → chunk → embed → store
- Handle errors and logging throughout process
- Provide progress updates
- Validate successful completion

## Quality Validation Checklist

### Phase 1 - Ingestion Validation
- [ ] All pages from sitemap are discovered and crawled
- [ ] Only content from specified domain is processed
- [ ] HTML tags and navigation elements are properly excluded
- [ ] Page metadata (title, URL, section) is preserved correctly
- [ ] Error handling for inaccessible pages is implemented

### Phase 2 - Chunking & Embeddings Validation
- [ ] All chunks are between 300-500 words
- [ ] Chunks respect sentence boundaries and section breaks
- [ ] Metadata is correctly associated with each chunk
- [ ] Cohere embeddings are successfully generated
- [ ] Embedding dimensions match expected size for embed-english-v3.0

### Phase 3 - Vector Storage Validation
- [ ] Qdrant collection "book_content" is created with correct configuration
- [ ] Vectors are stored with proper payload structure
- [ ] Cosine similarity configuration is applied
- [ ] All chunks are successfully stored in Qdrant
- [ ] Stored vectors can be retrieved and validated

### Overall Pipeline Validation
- [ ] End-to-end pipeline executes successfully
- [ ] Total execution time is within 2-hour limit for medium site
- [ ] 95% coverage of meaningful content is achieved
- [ ] 99% embedding success rate during normal operation
- [ ] Data integrity of 99.9% is maintained

## Testing Strategy

### Unit Tests
- Test individual functions in each module
- Mock external dependencies (Cohere API, Qdrant)
- Validate data transformations and business logic

### Integration Tests
- Test module interactions
- Validate end-to-end data flow
- Test error handling across components

### Performance Tests
- Measure execution time for different website sizes
- Test API rate limiting and batch processing
- Validate memory usage during processing

### Validation Tests
- Verify chunk size compliance (300-500 words)
- Confirm embedding dimensions match expected values
- Validate Qdrant storage format and retrieval

## Deployment & Environment Setup

### Development Setup
```bash
# Create backend directory
mkdir backend && cd backend

# Initialize project with uv
uv init

# Add dependencies
uv add requests beautifulsoup4 cohere qdrant-client python-dotenv

# Install development dependencies
uv add --dev pytest black mypy
```

### Required Dependencies
- `requests`: For HTTP requests and sitemap parsing
- `beautifulsoup4`: For HTML parsing and content extraction
- `cohere`: For embedding generation
- `qdrant-client`: For Qdrant database operations
- `python-dotenv`: For environment variable management
- `lxml`: For faster XML/HTML parsing (optional)

### Environment Configuration
Create `.env` file with:
```
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=http://localhost:6333  # or cloud URL
QDRANT_API_KEY=your_qdrant_api_key  # if using cloud
WEBSITE_URL=ai-humanoid-robots-hakathon.vercel.app
SITEMAP_URL=https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml
```

## Risk Analysis

### Technical Risks
- **API Rate Limits**: Cohere may rate-limit requests; implement batch processing and retry logic
- **Large Content**: Some pages may be extremely large; implement memory-efficient processing
- **Network Issues**: Handle timeouts and retries for HTTP requests
- **Qdrant Availability**: Implement connection pooling and error handling

### Data Quality Risks
- **Content Extraction**: HTML structure may vary; implement robust parsing with fallbacks
- **Chunk Boundaries**: Ensure chunks maintain semantic coherence
- **Metadata Loss**: Preserve all required metadata throughout pipeline

### Operational Risks
- **Execution Time**: Large sites may take longer than 2 hours; implement progress tracking
- **Storage Limits**: Monitor Qdrant storage capacity and costs
- **API Costs**: Track Cohere API usage and costs

## Success Criteria Verification

Each success criterion from the specification will be verified:
- **SC-001**: Measure content coverage during extraction
- **SC-002**: Validate chunk size distribution
- **SC-003**: Track embedding API success rate
- **SC-004**: Verify data integrity after storage
- **SC-005**: Time the complete pipeline execution
- **SC-006**: Perform sample semantic searches to verify precision