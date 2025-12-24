# Quickstart: Qdrant Retrieval Validation

## Setup

1. **Install dependencies** using uv:
   ```bash
   uv pip install python-dotenv qdrant-client cohere
   ```

2. **Configure environment variables**:
   Create a `.env` file with:
   ```env
   QDRANT_URL=https://your-cluster.qdrant.tech:6333
   QDRANT_API_KEY=your_qdrant_api_key
   COHERE_API_KEY=your_cohere_api_key
   QDRANT_COLLECTION_NAME=book_chunks
   ```

3. **Run the validation script**:
   ```bash
   python tests/test_qdrant_retrieval.py
   ```

## Expected Output

The script will:
1. Connect to Qdrant Cloud using environment configuration
2. Generate a Cohere embedding for the query "What is Physical AI?"
3. Perform similarity search against the book collection
4. Print 3-5 retrieved chunks with:
   - Similarity score
   - Text preview (first 200 characters)
   - Source reference
   - Full text content for inspection

## Validation Criteria

- Script runs without errors
- Returns 3-5 relevant chunks for the query
- Each result contains readable `text` and `source` fields
- Collection name, vector dimensions, and embeddings match ingestion
- Fails loudly with clear error messages if collection is empty or misconfigured