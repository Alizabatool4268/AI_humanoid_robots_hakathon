"""Qdrant storage operations module"""

from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Dict, Any, List
from src.config.settings import Settings
from src.logger import storage_logger


def create_collection(collection_name: str) -> bool:
    """
    Create a Qdrant collection with appropriate configuration.

    Args:
        collection_name: Name of the collection to create

    Returns:
        True if collection was created successfully
    """
    settings = Settings()

    # Initialize Qdrant client
    if settings.QDRANT_API_KEY:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=False  # Using HTTP for compatibility
        )
    else:
        client = QdrantClient(url=settings.QDRANT_URL)

    # Determine embedding dimensions based on Cohere model
    # embed-english-v3.0 typically produces 1024-dimensional vectors for search_document
    embedding_size = 1024  # Standard size for Cohere embed-english-v3.0

    try:
        # Check if collection already exists
        collections = client.get_collections().collections
        collection_names = [coll.name for coll in collections]

        if collection_name in collection_names:
            storage_logger.info(f"Collection '{collection_name}' already exists")
            return True

        # Create collection with cosine similarity
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=embedding_size,
                distance=models.Distance.COSINE
            )
        )

        storage_logger.info(f"Successfully created collection '{collection_name}' with cosine similarity")
        return True

    except Exception as e:
        storage_logger.error(f"Error creating collection '{collection_name}': {e}")
        return False


def save_chunk_to_qdrant(chunk: Dict, collection_name: str) -> bool:
    """
    Save a chunk with embedding to Qdrant collection.

    Args:
        chunk: Chunk with embedding and metadata
        collection_name: Name of the collection to save to

    Returns:
        True if chunk was saved successfully
    """
    settings = Settings()

    # Initialize Qdrant client
    if settings.QDRANT_API_KEY:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=False  # Using HTTP for compatibility
        )
    else:
        client = QdrantClient(url=settings.QDRANT_URL)

    try:
        # Prepare the payload
        payload = {
            "text": chunk['content'],
            "title": chunk['title'],
            "url": chunk['url'],
            "section": chunk['section'] if chunk['section'] else ""
        }

        # Prepare the point for insertion
        points = [
            models.PointStruct(
                id=chunk['id'],
                vector=chunk['vector'],
                payload=payload
            )
        ]

        # Upload the point to the collection
        client.upsert(
            collection_name=collection_name,
            points=points
        )

        storage_logger.debug(f"Successfully saved chunk {chunk['id']} to collection '{collection_name}'")
        return True

    except Exception as e:
        storage_logger.error(f"Error saving chunk {chunk['id']} to collection '{collection_name}': {e}")
        return False


def save_chunks_to_qdrant(chunks: List[Dict], collection_name: str) -> int:
    """
    Save multiple chunks to Qdrant collection efficiently.

    Args:
        chunks: List of chunks with embeddings and metadata
        collection_name: Name of the collection to save to

    Returns:
        Number of successfully saved chunks
    """
    settings = Settings()

    # Initialize Qdrant client
    if settings.QDRANT_API_KEY:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=False  # Using HTTP for compatibility
        )
    else:
        client = QdrantClient(url=settings.QDRANT_URL)

    try:
        # Prepare the points for insertion
        points = []
        for chunk in chunks:
            payload = {
                "text": chunk['content'],
                "title": chunk['title'],
                "url": chunk['url'],
                "section": chunk['section'] if chunk['section'] else ""
            }

            point = models.PointStruct(
                id=chunk['id'],
                vector=chunk['vector'],
                payload=payload
            )
            points.append(point)

        # Upload the points to the collection
        client.upsert(
            collection_name=collection_name,
            points=points
        )

        storage_logger.info(f"Successfully saved {len(points)} chunks to collection '{collection_name}'")
        return len(points)

    except Exception as e:
        storage_logger.error(f"Error saving {len(chunks)} chunks to collection '{collection_name}': {e}")
        return 0