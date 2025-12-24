from qdrant_client import QdrantClient
from qdrant_client.http import models
from config.settings import Settings
import logging
from typing import List, Dict, Any, Optional


def validate_collection_name(expected_collection_name: Optional[str] = None) -> bool:
    """
    Validate that the collection exists and matches the expected configuration.

    Args:
        expected_collection_name: Expected name of the collection (default: use settings)

    Returns:
        True if collection exists and name matches, False otherwise
    """
    if expected_collection_name is None:
        settings = Settings()
        expected_collection_name = settings.COLLECTION_NAME

    try:
        settings = Settings()
        # Initialize Qdrant client
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30.0
        )

        # Get list of all collections
        all_collections = client.get_collections()

        # Check if our expected collection exists
        collection_names = [col.name for col in all_collections.collections]

        if expected_collection_name in collection_names:
            logging.info(f"Collection '{expected_collection_name}' exists and matches expected configuration")
            return True
        else:
            logging.error(f"Collection '{expected_collection_name}' does not exist. Available collections: {collection_names}")
            return False

    except Exception as e:
        logging.error(f"Failed to validate collection name: {str(e)}")
        return False


def check_collection_exists_and_not_empty(collection_name: Optional[str] = None) -> bool:
    """
    Check if the specified collection exists and is not empty.

    Args:
        collection_name: Name of the collection to check (default: use settings)

    Returns:
        True if collection exists and has records, False otherwise
    """
    if collection_name is None:
        settings = Settings()
        collection_name = settings.COLLECTION_NAME

    try:
        settings = Settings()
        # Initialize Qdrant client
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30.0
        )

        # Get collection info
        collection_info = client.get_collection(collection_name)

        # Check if collection has points (records)
        if collection_info.points_count > 0:
            logging.info(f"Collection '{collection_name}' exists and has {collection_info.points_count} points")
            return True
        else:
            logging.warning(f"Collection '{collection_name}' exists but is empty (0 points)")
            return False

    except Exception as e:
        logging.error(f"Collection '{collection_name}' does not exist or is inaccessible: {str(e)}")
        return False


def perform_similarity_search(
    query_vector: List[float],
    limit: int = 5,
    collection_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Perform similarity search against the Qdrant collection using the provided query vector.

    Args:
        query_vector: The embedding vector to search for similar items
        limit: Maximum number of results to return (default: 5)
        collection_name: Name of the collection to search (default: use settings)

    Returns:
        List of search results with payload and similarity scores
    """
    if collection_name is None:
        settings = Settings()
        collection_name = settings.COLLECTION_NAME

    try:
        settings = Settings()
        # Initialize Qdrant client
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30.0
        )

        # Validate collection exists and is not empty
        if not check_collection_exists_and_not_empty(collection_name):
            raise ValueError(f"Collection '{collection_name}' is empty or does not exist")

        # Perform the search
        query_response = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,  # Include payload data
            with_vectors=False,  # We don't need the vectors back
            score_threshold=0.0  # Return all results above this threshold
        )

        # Format results from the QueryResponse object
        formatted_results = []
        for result in query_response.points:
            formatted_result = {
                'id': result.id,
                'score': result.score,
                'payload': result.payload
            }
            formatted_results.append(formatted_result)

        logging.info(f"Similarity search completed. Found {len(formatted_results)} results.")
        return formatted_results

    except Exception as e:
        logging.error(f"Failed to perform similarity search: {str(e)}")
        raise