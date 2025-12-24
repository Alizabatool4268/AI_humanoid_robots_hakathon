from qdrant_client import QdrantClient
from config.settings import Settings
import logging
from typing import Optional
import time
from functools import wraps


def retry_on_failure(max_retries=3, delay=1):
    """
    Decorator to retry a function on failure with exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logging.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
            raise last_exception
        return wrapper
    return decorator


@retry_on_failure(max_retries=3, delay=1)
def test_qdrant_connection() -> bool:
    """
    Test the Qdrant connection using environment configuration with retry logic.
    Returns True if connection is successful, False otherwise.
    """
    try:
        settings = Settings()
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30.0  # Increased timeout for robustness
        )

        # Try to get collections to verify connectivity
        collections = client.get_collections()
        logging.info(f"Successfully connected to Qdrant. Found {len(collections.collections)} collections")
        return True
    except Exception as e:
        logging.error(f"Qdrant connection test failed: {str(e)}")
        raise  # Re-raise to trigger retry


@retry_on_failure(max_retries=3, delay=1)
def get_qdrant_client_with_test() -> Optional[QdrantClient]:
    """
    Initialize Qdrant client and test connection with retry logic.
    Returns the client if successful, None if connection fails after retries.
    """
    try:
        settings = Settings()
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30.0  # Increased timeout for robustness
        )

        # Test the connection
        client.get_collections()
        return client
    except Exception as e:
        logging.error(f"Failed to initialize or connect to Qdrant: {str(e)}")
        raise  # Re-raise to trigger retry