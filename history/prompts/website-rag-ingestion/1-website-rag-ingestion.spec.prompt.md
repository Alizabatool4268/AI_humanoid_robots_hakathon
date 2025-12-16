---
id: 1
title: "Website RAG Ingestion Pipeline Specification"
stage: spec
date: 2025-12-17
surface: agent
model: Claude Sonnet 4.5
feature: website-rag-ingestion
branch: 1-website-rag-ingestion
user: user
command: /sp.specify
labels: ["rag", "vector-database", "content-ingestion", "specification"]
links:
  spec: "specs/1-website-rag-ingestion/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - "specs/1-website-rag-ingestion/spec.md"
  - "specs/1-website-rag-ingestion/checklists/requirements.md"
tests: []
---

# Prompt History Record: Website RAG Ingestion Pipeline Specification

## User Prompt

```
Website-based knowledge ingestion and vectorization pipeline for a book RAG chatbot

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
-siteMap url :ai-humanoid-robots-hakathon.vercel.app/sitemap.xml
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
- Qdrant collection populated with searchable book content
```

## Assistant Response

Created a comprehensive specification for the website-based knowledge ingestion and vectorization pipeline. The specification includes:

1. User Scenarios & Testing with 3 prioritized user stories covering content ingestion, chunking, and vector storage
2. Functional Requirements (14 specific requirements covering crawling, extraction, chunking, embedding, and storage)
3. Key Entities definitions for Text Chunk, Vector Embedding, Metadata, and Qdrant Collection
4. Success Criteria with 6 measurable outcomes

The specification follows the template structure and captures all the requirements from the user's feature description while maintaining focus on user value and business needs without implementation details.

A quality checklist was also created to validate the specification completeness.

## Outcome

Specification created successfully at specs/1-website-rag-ingestion/spec.md with comprehensive requirements for the RAG ingestion pipeline.