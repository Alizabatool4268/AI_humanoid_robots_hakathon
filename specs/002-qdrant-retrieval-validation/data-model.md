# Data Model: Qdrant Retrieval Validation

## Qdrant Payload Structure

The Qdrant collection contains book content chunks with the following payload structure:

### Text Chunk Entity
- **text** (string): The actual content chunk from the book
  - Required: Yes
  - Validation: Non-empty, readable text content
  - Max length: 1000 characters (approximate)

- **source** (string/object): Reference to the original document/chapter
  - Required: Yes
  - Validation: Valid URL or file reference
  - Format: Either direct URL to source or structured object with source metadata

- **chunk_id** (string): Unique identifier for the chunk
  - Required: Yes
  - Validation: Unique within collection
  - Format: UUID or similar unique identifier

### Vector Embedding
- **vector** (array of floats): Cohere-generated embedding
  - Required: Yes
  - Dimensions: 1024 (for Cohere embed-multilingual-v3.0)
  - Validation: Normalized vector (if using cosine similarity)

## Validation Output Structure

The script will output retrieved results in the following format:

### Retrieved Chunk
- **score** (float): Similarity score from Qdrant search
  - Range: 0.0 to 1.0 (for cosine similarity)
  - Validation: Non-negative value

- **text_preview** (string): First 200 characters of retrieved text
  - Max length: 200 characters
  - Validation: Readable content

- **source** (string): Source reference from payload
  - Validation: Non-empty, valid format

- **full_text** (string): Complete text content from payload
  - Validation: Non-empty, readable content

## Environment Configuration

### Required Environment Variables
- **QDRANT_URL** (string): URL for Qdrant Cloud instance
  - Required: Yes
  - Format: Valid HTTPS URL
  - Example: "https://your-cluster.qdrant.tech:6333"

- **QDRANT_API_KEY** (string): Authentication key for Qdrant Cloud
  - Required: Yes
  - Format: API key string
  - Security: Should be stored securely as environment variable

- **COHERE_API_KEY** (string): Authentication key for Cohere API
  - Required: Yes
  - Format: API key string
  - Security: Should be stored securely as environment variable

- **QDRANT_COLLECTION_NAME** (string): Name of the book collection
  - Required: Yes
  - Default: "book_chunks" (or similar)
  - Validation: Valid collection name format