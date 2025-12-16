# RAG Pipeline Setup Guide

## Prerequisites

- Python 3.8 or higher
- `uv` package manager installed
- Access to Cohere API (API key)
- Qdrant instance (local or cloud)

## Setup Instructions

### 1. Clone and Navigate to Backend Directory
```bash
# Already in backend directory
```

### 2. Install Dependencies
```bash
# Install dependencies using uv
uv sync

# Or install with development dependencies
uv sync --all-extras
```

### 3. Configure Environment Variables
Create a `.env` file in the backend directory with the following variables:
```bash
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=http://localhost:6333  # Use for local Qdrant
# QDRANT_URL=https://your-cluster-url.us-east-1-0.aws.cloud.qdrant.io  # Use for Qdrant Cloud
QDRANT_API_KEY=your_qdrant_api_key_here  # Required if using Qdrant Cloud
WEBSITE_URL=https://ai-humanoid-robots-hakathon.vercel.app
SITEMAP_URL=https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml
```

### 4. Set up Qdrant (Local Option)
If using local Qdrant, install and run via Docker:
```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## Running the Pipeline

### Execute the main pipeline:
```bash
python main.py
```

## Testing

### Run unit tests:
```bash
uv run pytest
```

### Run with specific test file:
```bash
uv run pytest tests/test_module.py
```