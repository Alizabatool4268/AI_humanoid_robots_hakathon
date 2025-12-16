# Feature Specification: Website-based Knowledge Ingestion and Vectorization Pipeline

**Feature Branch**: `1-website-rag-ingestion`
**Created**: 2025-12-17
**Status**: Draft
**Input**: User description: "Website-based knowledge ingestion and vectorization pipeline for a book RAG chatbot

Target audience:
AI engineers and hackathon evaluators reviewing a production-grade RAG system

Focus:
Transforming a published book website into a searchable vector knowledge base using Cohere embeddings and Qdrant. Do all the work in a separate backend folder.

Success criteria:
- Successfully ingests and cleans content from a given website URL
- Splits content into semantically meaningful chunks (300–500 words)
- Generates embeddings using Cohere (embed-english-v3.0)
- Stores vectors and metadata in a Qdrant collection
- Resulting vector database is ready for semantic search in a RAG chatbot

Constraints:
- Input source: Public website URL (Docusaurus book site)
- Embedding provider: Cohere
- Embedding model: embed-english-v3.0
- Vector database: Qdrant (cloud or local)
- Similarity metric: Cosine
- Output format: JSON-compatible objects
- Chunk size: 300–500 words


Data source:
- Website URL: ai-humanoid-robots-hakathon.vercel.app
- siteMap url :ai-humanoid-robots-hakathon.vercel.app/sitemap.xml
- Only content under this domain may be ingested
- No external or inferred content is allowed

Functional requirements:

PHASE 1 — DATA INGESTION
- Crawl all accessible pages under the provided website URL
- Extract only meaningful textual content:
  - Headings
  - Paragraphs
  - Lists
- Exclude:
  - Navigation menus
  - Footers and headers
  - Sidebars
  - Scripts, styles, and ads
- Preserve metadata for each page:
  - Page title
  - URL
  - Section or heading hierarchy

PHASE 2 — CHUNKING & EMBEDDINGS
- Normalize extracted content into plain text
- Split content into chunks of 300–500 words
- Ensure chunks do not break sentences or semantic sections
- Each chunk must retain parent metadata
- Generate embeddings using Cohere:
  - Model: embed-english-v3.0
  - One embedding per chunk
- Ensure the same embedding model will be reused for user queries at runtime

PHASE 3 — VECTOR STORAGE
- Create a Qdrant collection named: "book_content"
- Configure collection to match Cohere embedding dimensions
- Use cosine similarity for semantic search
- Store for each record:
  - Vector embedding
  - Original text chunk
  - Metadata (title, URL, section)

Output requirements:
- Each stored vector must follow this structure:

{
  "id": "<unique_chunk_id>",
  "vector": [<float values>],
  "payload": {
    "text": "<chunk text>",
    "title": "<page title>",
    "url": "<page url>",
    "section": "<section heading>"
  }
}

Non-goals:
- No chatbot UI
- No LLM-based question answering
- No ranking, reranking, or hybrid search
- No database other than Qdrant
- No fine-tuning of models

Assumptions:
- Website content is authoritative and static
- Embedding generation and vector storage are performed offline
- Output will later be consumed by a FastAPI-based RAG service

Deliverables:
- A clear, modular implementation plan or code scaffold
- Reproducible ingestion and embedding pipeline
- Qdrant collection populated with searchable book content"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ingest Website Content for RAG System (Priority: P1)

An AI engineer needs to transform a published book website into a searchable vector knowledge base that can be used for a RAG chatbot. The engineer provides the website URL and expects the system to crawl, extract, and convert the content into a format suitable for semantic search.

**Why this priority**: This is the core functionality that enables the entire RAG system - without ingested content, there is no knowledge base to search against.

**Independent Test**: The system can successfully crawl the website ai-humanoid-robots-hakathon.vercel.app, extract meaningful content, and store it in a vector database ready for semantic search.

**Acceptance Scenarios**:

1. **Given** a valid website URL (ai-humanoid-robots-hakathon.vercel.app), **When** the ingestion pipeline is executed, **Then** all accessible pages are crawled and meaningful content is extracted while excluding navigation, footers, and scripts.

2. **Given** crawled webpage content, **When** the extraction process runs, **Then** only headings, paragraphs, and lists are retained while navigation elements are filtered out.

3. **Given** extracted content with metadata, **When** the pipeline processes it, **Then** the original page title, URL, and section hierarchy are preserved.

---

### User Story 2 - Transform Content into Semantic Chunks (Priority: P1)

An AI engineer needs to split the extracted website content into semantically meaningful chunks of 300-500 words that maintain context and readability for later semantic search operations.

**Why this priority**: Proper chunking is essential for effective semantic search - chunks that are too large lose specificity, while chunks that are too small break context.

**Independent Test**: The system can take raw extracted content and split it into appropriately sized chunks (300-500 words) without breaking sentences or semantic sections.

**Acceptance Scenarios**:

1. **Given** extracted content from a webpage, **When** the chunking algorithm processes it, **Then** chunks are between 300-500 words in length.

2. **Given** content with logical section breaks, **When** chunking occurs, **Then** chunks respect section boundaries and don't split sentences mid-sentence.

3. **Given** a chunk of text, **When** the process completes, **Then** the original metadata (title, URL, section) is associated with each chunk.

---

### User Story 3 - Generate and Store Vector Embeddings (Priority: P2)

An AI engineer needs to convert text chunks into vector embeddings using Cohere's embed-english-v3.0 model and store them in a Qdrant vector database for semantic search capabilities.

**Why this priority**: This enables the core semantic search functionality that makes the RAG system valuable - the ability to find relevant content based on meaning rather than exact keyword matches.

**Independent Test**: The system can generate embeddings for text chunks using Cohere's model and store them in Qdrant with associated metadata.

**Acceptance Scenarios**:

1. **Given** a text chunk, **When** the embedding process runs, **Then** a vector is generated using Cohere's embed-english-v3.0 model.

2. **Given** generated embeddings with metadata, **When** they are stored in Qdrant, **Then** they are saved in a "book_content" collection with proper cosine similarity configuration.

3. **Given** stored embeddings in Qdrant, **When** queried, **Then** they maintain the structure specified in the requirements with id, vector, and payload containing text, title, URL, and section.

---

### Edge Cases

- What happens when the website crawler encounters pages that require authentication or are blocked by robots.txt?
- How does the system handle pages with extremely large content that might exceed memory limitations during processing?
- What occurs when the Cohere API is temporarily unavailable during the embedding generation phase?
- How does the system handle malformed HTML or JavaScript-heavy pages that may not render properly for content extraction?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST crawl all accessible pages under the provided website URL (ai-humanoid-robots-hakathon.vercel.app)
- **FR-002**: System MUST extract only meaningful textual content including headings, paragraphs, and lists
- **FR-003**: System MUST exclude navigation menus, footers, headers, sidebars, scripts, styles, and ads from extraction
- **FR-004**: System MUST preserve metadata for each page including page title, URL, and section or heading hierarchy
- **FR-005**: System MUST normalize extracted content into plain text format
- **FR-006**: System MUST split content into chunks of 300-500 words without breaking sentences or semantic sections
- **FR-007**: System MUST retain parent metadata for each chunk during the splitting process
- **FR-008**: System MUST generate embeddings using Cohere's embed-english-v3.0 model with one embedding per chunk
- **FR-009**: System MUST create a Qdrant collection named "book_content" with cosine similarity configuration
- **FR-010**: System MUST store vector embeddings, original text chunks, and metadata in the Qdrant collection
- **FR-011**: System MUST ensure the same embedding model (embed-english-v3.0) will be reused for user queries at runtime
- **FR-012**: System MUST follow the specified output structure with id, vector, and payload containing text, title, URL, and section
- **FR-013**: System MUST process content only from the specified domain (ai-humanoid-robots-hakathon.vercel.app) without external content
- **FR-014**: System MUST use the sitemap URL (ai-humanoid-robots-hakathon.vercel.app/sitemap.xml) to discover pages to crawl

### Key Entities

- **Text Chunk**: A segment of website content (300-500 words) that maintains semantic coherence and includes associated metadata
- **Vector Embedding**: Numerical representation of text content generated by Cohere's embed-english-v3.0 model for semantic similarity calculations
- **Metadata**: Information about the source of content including page title, URL, and hierarchical section information
- **Qdrant Collection**: Vector database storage structure named "book_content" configured for cosine similarity search operations

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Successfully ingest and clean content from all accessible pages under ai-humanoid-robots-hakathon.vercel.app with 95% coverage of meaningful content
- **SC-002**: Split content into semantically meaningful chunks of 300-500 words with 90% maintaining proper sentence and section boundaries
- **SC-003**: Generate embeddings using Cohere embed-english-v3.0 model with 99% success rate during normal API availability
- **SC-004**: Store vectors and metadata in Qdrant collection with 99.9% data integrity and proper structure compliance
- **SC-005**: Complete the entire ingestion pipeline (crawl, extract, chunk, embed, store) within 2 hours for a medium-sized website (100-500 pages)
- **SC-006**: Result in a vector database ready for semantic search that can return relevant results with 85% precision for sample queries