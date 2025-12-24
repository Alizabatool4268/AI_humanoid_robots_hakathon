#!/usr/bin/env python3
"""
Test script to list all content in the Qdrant collection.
"""

import sys
import os
# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging
from qdrant_client import QdrantClient
from config.settings import Settings


def main():
    """
    Main function to list all content in the Qdrant collection.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        # Load settings with validation
        settings = Settings()
        settings.validate()  # Validate required settings
        logging.info(f"Settings loaded successfully. Qdrant URL: {settings.QDRANT_URL}")

        # Initialize Qdrant client
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30.0
        )

        # Get collection info
        collection_info = client.get_collection(settings.COLLECTION_NAME)
        logging.info(f"Collection '{settings.COLLECTION_NAME}' has {collection_info.points_count} points")

        # Retrieve a few points to see what content exists
        logging.info("Retrieving sample points from the collection...")

        # Use scroll to get some points from the collection
        points, next_page = client.scroll(
            collection_name=settings.COLLECTION_NAME,
            limit=5,  # Get first 5 points
            with_payload=True,
            with_vectors=False
        )

        logging.info(f"Retrieved {len(points)} sample points from the collection:")

        for i, point in enumerate(points, 1):
            payload = point.payload
            print(f"\nPoint {i}:")
            print(f"  ID: {point.id}")
            print(f"  Payload keys: {list(payload.keys()) if payload else 'None'}")
            if 'text' in payload:
                text_preview = payload['text'][:200] + "..." if len(payload['text']) > 200 else payload['text']
                print(f"  Text preview: {text_preview}")
            if 'source' in payload:
                print(f"  Source: {payload['source']}")
            if 'title' in payload:
                print(f"  Title: {payload['title']}")
            if 'url' in payload:
                print(f"  URL: {payload['url']}")

        logging.info("Collection content listing completed.")
        return 0

    except Exception as e:
        # Handle errors
        logging.error(f"An error occurred while listing collection content: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())