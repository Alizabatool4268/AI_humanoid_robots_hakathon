import cohere
from .config.settings import Settings
import logging


def get_cohere_client():
    """
    Initialize and return a Cohere client using the API key from environment configuration.
    """
    try:
        settings = Settings()
        client = cohere.Client(
            api_key=settings.COHERE_API_KEY
        )
        logging.info("Cohere client initialized successfully")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Cohere client: {str(e)}")
        raise