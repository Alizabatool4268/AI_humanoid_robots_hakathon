# Quickstart Guide: Website-based Knowledge Ingestion Pipeline

**Feature**: 1-website-rag-ingestion
**Created**: 2025-12-17

## Prerequisites

- Python 3.10 or higher
- `uv` package manager installed
- Access to Cohere API (API key)
- Qdrant instance (local or cloud)

## Setup Instructions

### 1. Clone and Navigate to Backend Directory
```bash
# Create backend directory if it doesn't exist
mkdir backend
cd backend
```

### 2. Initialize Python Project with uv
```bash
# Initialize new project
uv init

# Or if starting fresh in backend directory
uv init .
```

### 3. Install Dependencies
```bash
# Add required packages
uv add requests beautifulsoup4 cohere qdrant-client python-dotenv lxml

# Add development dependencies
uv add --dev pytest black mypy
```

### 4. Create Environment File
Create a `.env` file in the backend directory:
```bash
# .env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=http://localhost:6333  # Use for local Qdrant
# QDRANT_URL=https://your-cluster-url.us-east-1-0.aws.cloud.qdrant.io  # Use for Qdrant Cloud
QDRANT_API_KEY=your_qdrant_api_key_here  # Required if using Qdrant Cloud
WEBSITE_URL=https://ai-humanoid-robots-hakathon.vercel.app
SITEMAP_URL=https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml
```

### 5. Set up Qdrant (Local Option)
If using local Qdrant, install and run via Docker:
```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## Running the Pipeline

### 1. Create the main.py file with the following structure:
```python
# main.py
import asyncio
from src.crawler import get_all_urls
from src.extractor import extract_text_from_url
from src.chunker import chunk_text
from src.embedder import embed
from src.storage import create_collection, save_chunk_to_qdrant

async def main():
    """
    Main pipeline execution: crawl → extract → chunk → embed → store
    """
    print("Starting RAG ingestion pipeline...")

    # Phase 1: Crawl website
    print("Phase 1: Crawling website...")
    urls = get_all_urls(
        base_url="https://ai-humanoid-robots-hakathon.vercel.app",
        sitemap_url="https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml"
    )
    print(f"Discovered {len(urls)} URLs")

    # Phase 2: Extract content from each URL
    print("Phase 2: Extracting content...")
    all_chunks = []
    for url in urls:
        try:
            content_data = extract_text_from_url(url)
            chunks = chunk_text(
                content_data["content"],
                url,
                content_data["title"],
                content_data["section_hierarchy"]
            )
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    print(f"Created {len(all_chunks)} text chunks")

    # Phase 3: Generate embeddings
    print("Phase 3: Generating embeddings...")
    chunks_with_embeddings = embed(all_chunks)
    print(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")

    # Phase 4: Create Qdrant collection and store vectors
    print("Phase 4: Creating Qdrant collection and storing vectors...")
    collection_name = "book_content"
    create_collection(collection_name)

    success_count = 0
    for chunk in chunks_with_embeddings:
        try:
            success = save_chunk_to_qdrant(chunk, collection_name)
            if success:
                success_count += 1
        except Exception as e:
            print(f"Error saving chunk to Qdrant: {e}")

    print(f"Successfully stored {success_count} out of {len(chunks_with_embeddings)} chunks in Qdrant")
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Create the required modules in the src/ directory

Create the directory structure:
```bash
mkdir src
touch src/__init__.py
touch src/crawler.py
touch src/extractor.py
touch src/chunker.py
touch src/embedder.py
touch src/storage.py
```

### 3. Run the Pipeline
```bash
# From the backend directory
python main.py
```

## Testing the Setup

### Basic Test
```bash
# Test that dependencies are installed correctly
python -c "import requests, bs4, cohere, qdrant_client; print('All dependencies available')"
```

### Environment Test
```bash
# Test environment variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('COHERE_API_KEY available:', bool(os.getenv('COHERE_API_KEY')))"
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   - Solution: Run `uv sync` to ensure all dependencies are installed

2. **Environment Variables Not Loading**:
   - Solution: Ensure `.env` file is in the correct directory and properly formatted

3. **Cohere API Issues**:
   - Solution: Verify API key is correct and has proper permissions

4. **Qdrant Connection Issues**:
   - Solution: Check that Qdrant is running and URL/API key are correct

5. **Rate Limiting**:
   - Solution: The pipeline should handle rate limits automatically, but verify API usage limits

## Next Steps

1. Review the generated logs to confirm successful pipeline execution
2. Verify the "book_content" collection exists in Qdrant with the expected number of vectors
3. Test semantic search functionality using the stored vectors
4. Monitor API usage for Cohere and Qdrant to ensure within limits