# Contract: Qdrant Retrieval Validation Script

## Script Interface

The validation script `test_qdrant_retrieval.py` operates as a command-line utility with no input parameters required. It follows this execution pattern:

### Execution
```bash
python tests/test_qdrant_retrieval.py
```

### Input
- Environment variables (loaded from .env or system):
  - `QDRANT_URL`: Qdrant Cloud endpoint
  - `QDRANT_API_KEY`: Authentication key for Qdrant
  - `COHERE_API_KEY`: Authentication key for Cohere
  - `QDRANT_COLLECTION_NAME`: Name of the book collection

### Processing
1. Connect to Qdrant Cloud using environment configuration
2. Generate Cohere embedding for the fixed query: "What is Physical AI?"
3. Perform similarity search against the specified collection
4. Validate that results meet the required criteria

### Output
- **Success case**: Print 3-5 retrieved chunks in the format:
  ```
  Score: {similarity_score}
  Source: {source_reference}
  Text Preview: {first_200_chars}
  Full Text: {complete_text_content}
  ---
  ```
- **Failure case**: Exit with error code and descriptive error message

### Error Conditions
- Qdrant connection failure → Exit code 1 with connection error
- Cohere API failure → Exit code 1 with embedding error
- Empty collection → Exit code 1 with "collection is empty" message
- Invalid configuration → Exit code 1 with configuration error
- No results for query → Exit code 1 with "no relevant chunks found" message