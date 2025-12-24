# Research: Qdrant Retrieval Validation

## Decision: Cohere Embedding Model Selection

**What was chosen**: Cohere's embed-multilingual-v3.0 model (1024 dimensions)

**Rationale**:
- Good for technical content including AI/robotics concepts
- Multilingual support for potential Roman Urdu translation
- Standard model with good performance for retrieval tasks
- Aligns with project's minimal compute constraint

**Alternatives considered**:
- OpenAI's text-embedding-3-small (1536 dimensions) - rejected due to potential cost concerns
- SentenceTransformer models - rejected as they require local compute, violating minimal compute principle
- Cohere embed-english-v3.0 - rejected as multilingual support better for future translation features

## Decision: Qdrant Similarity Metric

**What was chosen**: Cosine similarity

**Rationale**:
- Standard for embedding similarity searches
- Well-suited for text retrieval tasks
- Efficient for high-dimensional vector spaces
- Default in Qdrant for semantic search

**Alternatives considered**:
- Euclidean distance - less appropriate for high-dimensional embeddings
- Dot product - sensitive to vector magnitude, not just direction
- Manhattan distance - less common for embedding similarity

## Decision: Result Limit

**What was chosen**: Top 3-5 results

**Rationale**:
- Matches user requirement specification
- Provides sufficient context without overwhelming output
- Good balance between information density and readability
- Aligns with typical RAG retrieval patterns

**Alternatives considered**:
- Single result - insufficient context for validation
- 10+ results - too verbose for validation script
- Variable count based on confidence scores - adds unnecessary complexity

## Decision: Payload Field Names

**What was chosen**:
- `text` field for the content chunk
- `source` field for document reference/metadata

**Rationale**:
- Matches requirements from feature specification
- Clear, descriptive names for validation output
- Consistent with common RAG implementation patterns
- Easy to parse and inspect manually

**Alternatives considered**:
- `content` instead of `text` - decided `text` is more specific to textual content
- `metadata` or `doc_source` instead of `source` - `source` is more concise and clear

## Technical Implementation Approach

**Environment Configuration**:
- Use python-dotenv to load Qdrant Cloud credentials
- Load Cohere API key from environment variables
- Follow existing project patterns for settings management

**Query Processing**:
- Use Cohere API to generate embedding for the query "What is Physical AI?"
- Perform search against the book collection in Qdrant
- Retrieve with payload to access text and source fields

**Output Format**:
- Print chunk text preview (first 200 characters)
- Show similarity score
- Display source information
- Fail with clear error if no results returned