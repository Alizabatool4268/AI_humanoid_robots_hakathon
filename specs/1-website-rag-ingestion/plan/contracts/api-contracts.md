# API Contracts: Website-based Knowledge Ingestion Pipeline

**Feature**: 1-website-rag-ingestion
**Created**: 2025-12-17
**Status**: Draft

## Internal Module Interfaces

### Crawler Module Interface (`src/crawler.py`)

#### Function: `get_all_urls(base_url: str, sitemap_url: str) -> List[str]`

**Description**: Discovers and returns all accessible URLs from the specified website using the sitemap.

**Parameters**:
- `base_url` (string): The base URL of the website to crawl
- `sitemap_url` (string): The URL of the sitemap.xml file

**Returns**:
- `List[str]`: List of all discovered page URLs within the specified domain

**Errors**:
- NetworkError: When unable to access sitemap or network issues occur
- InvalidURLError: When provided URLs are malformed
- DomainViolationError: When discovered URLs are outside the specified domain

**Example**:
```python
urls = get_all_urls(
    base_url="https://ai-humanoid-robots-hakathon.vercel.app",
    sitemap_url="https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml"
)
# Returns: ["https://ai-humanoid-robots-hakathon.vercel.app/page1", ...]
```

### Extractor Module Interface (`src/extractor.py`)

#### Function: `extract_text_from_url(url: str) -> Dict[str, Any]`

**Description**: Extracts meaningful content from a single webpage URL.

**Parameters**:
- `url` (string): The URL of the webpage to extract content from

**Returns**:
- `Dict[str, Any]` with keys:
  - `title` (string): Page title from HTML
  - `content` (string): Extracted text content (headings, paragraphs, lists)
  - `section_hierarchy` (List[str]): Hierarchy of headings/sections

**Errors**:
- NetworkError: When unable to access the URL
- ContentExtractionError: When content extraction fails
- InvalidURLError: When the URL is malformed

**Example**:
```python
content_data = extract_text_from_url("https://ai-humanoid-robots-hakathon.vercel.app/introduction")
# Returns: {
#     "title": "Introduction - AI Humanoid Robots",
#     "content": "This book covers...",
#     "section_hierarchy": ["Home", "Introduction"]
# }
```

### Chunker Module Interface (`src/chunker.py`)

#### Function: `chunk_text(text: str, url: str, title: str, section: str) -> List[Dict]`

**Description**: Splits text content into semantically meaningful chunks of 300-500 words.

**Parameters**:
- `text` (string): Raw text content to be chunked
- `url` (string): Source URL of the content
- `title` (string): Page title
- `section` (str): Section/heading hierarchy

**Returns**:
- `List[Dict]` where each dict contains:
  - `id` (string): Unique chunk identifier
  - `content` (string): Chunk text content
  - `url` (string): Source URL
  - `title` (string): Page title
  - `section` (string): Section/heading
  - `word_count` (int): Number of words in chunk

**Errors**:
- InvalidInputError: When text input is invalid
- ChunkingError: When chunking process fails

**Example**:
```python
chunks = chunk_text("Long text content...", "https://example.com", "Page Title", "Section 1")
# Returns: [
#     {
#         "id": "chunk-uuid-1",
#         "content": "First 400 words of content...",
#         "url": "https://example.com",
#         "title": "Page Title",
#         "section": "Section 1",
#         "word_count": 400
#     },
#     ...
# ]
```

### Embedder Module Interface (`src/embedder.py`)

#### Function: `embed(chunks: List[Dict]) -> List[Dict]`

**Description**: Generates Cohere embeddings for text chunks.

**Parameters**:
- `chunks` (List[Dict]): List of text chunks to embed

**Returns**:
- `List[Dict]`: Same chunks with added embedding vectors:
  - All original fields
  - `vector` (List[float]): Embedding vector values
  - `embedding_model` (string): Model used ("embed-english-v3.0")

**Errors**:
- APIError: When Cohere API is unavailable or returns error
- AuthenticationError: When API key is invalid
- RateLimitError: When API rate limits are exceeded

**Example**:
```python
chunks_with_embeddings = embed([
    {
        "id": "chunk-1",
        "content": "Text content...",
        # ... other fields
    }
])
# Returns: [
#     {
#         "id": "chunk-1",
#         "content": "Text content...",
#         "vector": [0.1, 0.3, ...],  # 1024+ dimensional vector
#         "embedding_model": "embed-english-v3.0"
#     }
# ]
```

### Storage Module Interface (`src/storage.py`)

#### Function: `create_collection(collection_name: str) -> bool`

**Description**: Creates a Qdrant collection with appropriate configuration.

**Parameters**:
- `collection_name` (string): Name of the collection to create

**Returns**:
- `bool`: True if collection was created successfully

**Errors**:
- StorageError: When collection creation fails
- ConfigurationError: When configuration is invalid

**Example**:
```python
success = create_collection("book_content")
# Returns: True
```

#### Function: `save_chunk_to_qdrant(chunk: Dict, collection_name: str) -> bool`

**Description**: Saves a chunk with embedding to Qdrant collection.

**Parameters**:
- `chunk` (Dict): Chunk with embedding and metadata
- `collection_name` (string): Name of the collection to save to

**Returns**:
- `bool`: True if chunk was saved successfully

**Errors**:
- StorageError: When storage operation fails
- ValidationError: When chunk format is invalid

**Example**:
```python
success = save_chunk_to_qdrant({
    "id": "chunk-1",
    "vector": [0.1, 0.3, ...],
    "payload": {
        "text": "chunk content",
        "title": "page title",
        "url": "https://example.com",
        "section": "section name"
    }
}, "book_content")
# Returns: True
```

## Configuration Contract

### Environment Variables

The system expects the following environment variables:

#### Required Variables:
- `COHERE_API_KEY` (string): API key for Cohere embedding service
- `WEBSITE_URL` (string): Base URL to crawl (default: https://ai-humanoid-robots-hakathon.vercel.app)
- `SITEMAP_URL` (string): Sitemap URL (default: https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml)

#### Optional Variables:
- `QDRANT_URL` (string): URL for Qdrant instance (default: http://localhost:6333)
- `QDRANT_API_KEY` (string): API key for Qdrant (if using cloud service)
- `CHUNK_MIN_WORDS` (int): Minimum words per chunk (default: 300)
- `CHUNK_MAX_WORDS` (int): Maximum words per chunk (default: 500)
- `COHERE_MODEL` (string): Embedding model name (default: embed-english-v3.0)

## Data Format Contracts

### Input/Output Formats

#### Source Webpage Format (Internal):
```json
{
  "url": "string",
  "title": "string",
  "content": "string",
  "section_hierarchy": ["string"]
}
```

#### Text Chunk Format (Internal):
```json
{
  "id": "string",
  "content": "string",
  "url": "string",
  "title": "string",
  "section": "string",
  "word_count": "int"
}
```

#### Embedded Chunk Format (Internal):
```json
{
  "id": "string",
  "content": "string",
  "url": "string",
  "title": "string",
  "section": "string",
  "word_count": "int",
  "vector": ["float"],
  "embedding_model": "string"
}
```

#### Qdrant Record Format (Storage):
```json
{
  "id": "string",
  "vector": ["float"],
  "payload": {
    "text": "string",
    "title": "string",
    "url": "string",
    "section": "string"
  }
}
```

## Error Handling Contract

### Standard Error Types

All modules should raise appropriate exceptions following these patterns:

- `NetworkError`: For network-related issues
- `AuthenticationError`: For authentication failures
- `ValidationError`: For data validation failures
- `ConfigurationError`: For configuration issues
- `RateLimitError`: For API rate limiting
- `StorageError`: For storage-related issues

### Error Response Format
```json
{
  "error_type": "string",
  "message": "string",
  "details": "object (optional)"
}
```