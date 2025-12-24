from typing import List, Dict, Any
from embedding_generator import generate_cohere_embedding
from qdrant_search import perform_similarity_search
import logging


def retrieve_chunks(
    query: str = "What is Physical AI?",
    result_limit: int = 5,
    min_results: int = 3
) -> List[Dict[str, Any]]:
    """
    Core retrieval function that combines Cohere embedding generation with Qdrant search.

    Args:
        query: The query text to search for (default: "What is Physical AI?")
        result_limit: Maximum number of results to retrieve (default: 5)
        min_results: Minimum number of results expected (default: 3)

    Returns:
        List of retrieved chunks with scores and payloads
    """
    try:
        logging.info(f"Starting retrieval for query: '{query}'")

        # Generate embedding for the query using Cohere
        query_embedding = generate_cohere_embedding(query)
        logging.info(f"Generated embedding with {len(query_embedding)} dimensions")

        # Perform similarity search in Qdrant
        search_results = perform_similarity_search(
            query_vector=query_embedding,
            limit=result_limit
        )

        # Validate we have the expected number of results
        if len(search_results) < min_results:
            logging.warning(
                f"Expected at least {min_results} results, but got {len(search_results)}. "
                f"This might indicate insufficient relevant content in the collection."
            )

        logging.info(f"Retrieved {len(search_results)} chunks for query: '{query}'")
        return search_results

    except Exception as e:
        logging.error(f"Failed to retrieve chunks: {str(e)}")
        raise