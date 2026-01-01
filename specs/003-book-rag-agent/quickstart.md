# Quickstart Guide: Backend Multi-Agent System for Book RAG Chatbot

**Feature**: 003-book-rag-agent
**Date**: 2025-12-31

## Overview

This guide provides the essential steps to set up and run the Backend Multi-Agent System for Book RAG Chatbot.

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Access to Qdrant Cloud (Free Tier)
- Cohere API key
- Google AI API key for Gemini
- OpenAI API key (if required by agents SDK)

## Installation

1. **Install UV package manager** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Create and navigate to backend directory**:
   ```bash
   mkdir -p backend
   cd backend
   ```

3. **Create requirements.txt**:
   ```txt
   openai-agents
   cohere
   qdrant-client
   google-generativeai
   python-dotenv
   ```

4. **Install dependencies using UV**:
   ```bash
   uv pip install -r requirements.txt
   ```

## Environment Configuration

Create a `.env` file in the backend directory with the following:

```env
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
COHERE_API_KEY=your_cohere_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key  # if required by agents SDK
```

## Qdrant Setup

1. **Create a Qdrant collection** for book embeddings:
   ```python
   from qdrant_client import QdrantClient
   import os

   client = QdrantClient(
       url=os.getenv("QDRANT_URL"),
       api_key=os.getenv("QDRANT_API_KEY")
   )

   # Create collection for book content
   client.recreate_collection(
       collection_name="book_content",
       vectors_config={
           "size": 1024,  # Cohere embedding size
           "distance": "Cosine"
       }
   )
   ```

## Running the Agent System

1. **Start the backend agent**:
   ```bash
   python -c "from agents import run_agent_system; run_agent_system()"
   ```

2. **Test the system with a simple query**:
   ```bash
   curl -X POST http://localhost:8000/api/agent/query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What is the main theme of the book?",
       "selected_text": ""
     }'
   ```

## Basic Usage Examples

### Example 1: Basic Book Query
```python
from agents import process_query

response = process_query({
    "query": "Explain the main character's motivation",
    "selected_text": ""
})
print(response["answer"])
```

### Example 2: Query with Selected Text Override
```python
response = process_query({
    "query": "What does this passage mean?",
    "selected_text": "The main character struggled with his identity throughout the novel..."
})
print(response["answer"])
```

## Development Workflow

1. **Implement the triage agent** in `backend/agents.py`
2. **Implement the query agent** in the same file
3. **Test agent handoff** functionality
4. **Validate RAG responses** are properly grounded
5. **Run unit tests** to ensure all requirements are met

## Testing

Run the test suite:
```bash
pytest tests/test_agents.py
```

The test suite includes:
- Intent classification validation
- Agent handoff verification
- Selected text override functionality
- Response grounding verification
- Performance benchmarks

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Verify all API keys are correctly set in `.env`
2. **Slow Response Times**: Check Qdrant collection size and embedding quality
3. **Poor Retrieval Quality**: Verify book content was properly embedded in Qdrant

### Debugging Tips

- Enable logging to see agent decision-making process
- Check that Cohere embeddings match Qdrant vector dimensions
- Verify Gemini API responses follow expected format