# Configuration Management for RAG Pipeline

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
class Settings:
    """Configuration settings for the RAG pipeline"""

    # Website source configuration
    WEBSITE_URL: str = os.getenv(
        "WEBSITE_URL",
        "https://ai-humanoid-robots-hakathon.vercel.app"
    )

    SITEMAP_URL: str = os.getenv(
        "SITEMAP_URL",
        "https://ai-humanoid-robots-hakathon.vercel.app/sitemap.xml"
    )

    # Cohere configuration
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "embed-english-v3.0")

    # Qdrant configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY", None)
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "book_content")

    # Chunking configuration
    CHUNK_MIN_WORDS: int = int(os.getenv("CHUNK_MIN_WORDS", "300"))
    CHUNK_MAX_WORDS: int = int(os.getenv("CHUNK_MAX_WORDS", "500"))

    # Processing configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))  # For embedding API calls
    REQUEST_DELAY: float = float(os.getenv("REQUEST_DELAY", "1.0"))  # Delay between requests in seconds

    # Validation
    def validate(self) -> bool:
        """Validate that required settings are present"""
        if not self.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable is required")
        return True