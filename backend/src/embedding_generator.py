import cohere
from config.settings import Settings
import logging
from typing import List


def validate_vector_dimensions(embedding_vector: List[float], expected_dimension: int = 1024) -> bool:
    """
    Validate that the embedding vector has the expected dimensions.

    Args:
        embedding_vector: The embedding vector to validate
        expected_dimension: Expected number of dimensions (default: 1024 for Cohere multilingual model)

    Returns:
        True if dimensions match expected value, False otherwise
    """
    actual_dimension = len(embedding_vector)
    if actual_dimension == expected_dimension:
        logging.info(f"Vector dimension validation passed: {actual_dimension} dimensions as expected")
        return True
    else:
        logging.error(f"Vector dimension validation failed: expected {expected_dimension}, got {actual_dimension}")
        return False


def generate_cohere_embedding(query_text: str = "What is Physical AI?") -> List[float]:
    """
    Generate a Cohere embedding for the given query text.

    Args:
        query_text: The text to generate an embedding for (default: "What is Physical AI?")

    Returns:
        A list of floats representing the embedding vector
    """
    try:
        settings = Settings()
        # Initialize Cohere client
        co = cohere.Client(api_key=settings.COHERE_API_KEY)

        # Generate embedding
        response = co.embed(
            texts=[query_text],
            model='embed-multilingual-v3.0',  # Using the model specified in data model
            input_type="search_query"
        )

        # Extract the embedding vector
        embedding_vector = response.embeddings[0]  # Get the first (and only) embedding

        logging.info(f"Successfully generated embedding for query: '{query_text}'")
        logging.info(f"Embedding dimensions: {len(embedding_vector)}")

        # Validate vector dimensions
        if not validate_vector_dimensions(embedding_vector, 1024):
            logging.warning("Embedding dimensions do not match expected 1024 dimensions")

        return embedding_vector

    except Exception as e:
        logging.error(f"Failed to generate Cohere embedding: {str(e)}")
        raise