#!/usr/bin/env python3
"""
Qdrant Retrieval Validation Script

This script validates the retrieval of embedded book content from Qdrant
using the query "What is Physical AI?".
"""

import sys
import os
# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging
from typing import List, Dict, Any


def main():
    """
    Main function to execute the Qdrant retrieval validation.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        # Import modules
        from config.settings import Settings
        from connection_test import test_qdrant_connection
        from retrieval import retrieve_chunks
        from result_formatter import print_retrieved_results
        from payload_validator import validate_retrieved_payloads

        # Load settings with validation
        settings = Settings()
        settings.validate()  # Validate required settings
        logging.info(f"Settings loaded successfully. Qdrant URL: {settings.QDRANT_URL}")

        # Phase 1: Validate Qdrant connection
        logging.info("Starting Qdrant connection validation...")
        connection_success = test_qdrant_connection()
        if not connection_success:
            logging.error("Qdrant connection test failed. Exiting.")
            sys.exit(1)
        logging.info("Qdrant connection validation completed successfully.")

        # Phase 2: Retrieve book data using Cohere embeddings
        logging.info("Starting retrieval validation with query: 'What is ros2-fundamentals?'")

        # Retrieve chunks for the target query
        results = retrieve_chunks(
            query="What is ros2-fundamentals?",
            result_limit=5,
            min_results=3
        )

        # Validate that we got the expected number of results (3-5)
        result_count = len(results)
        logging.info(f"Retrieved {result_count} chunks for the query")

        if 3 <= result_count <= 5:
            logging.info(f"✓ Successfully retrieved {result_count} relevant chunks (within expected range 3-5)")
        else:
            logging.warning(f"⚠ Retrieved {result_count} chunks, which is outside the expected range of 3-5")

        # Print retrieved results if any were found
        if results:
            logging.info("Displaying retrieved results:")
            print_retrieved_results(results)
        else:
            logging.info("No relevant results found for the query 'What is ros2-fundamentals?'")
            logging.info("This may be because the collection doesn't contain content about Physical AI.")

        # Validate payload structure
        payload_validation_success = validate_retrieved_payloads(results)
        if not payload_validation_success:
            logging.error("Payload validation failed. Some results are missing required 'text' or 'source' fields.")
            sys.exit(1)
        else:
            logging.info("✓ All retrieved payloads have valid structure with required 'text' and 'source' fields")

        # Display the results using the formatter
        print_retrieved_results(results)

        logging.info("Qdrant retrieval validation completed successfully.")
        return 0

    except ValueError as e:
        # Handle missing environment variables or validation errors
        logging.error(f"Configuration or validation error: {str(e)}")
        if "empty or does not exist" in str(e):
            logging.error("Collection is empty or misconfigured. The script fails loudly as required.")
        else:
            logging.error("Please check your environment variables or .env file.")
        sys.exit(1)
    except Exception as e:
        # Handle other errors
        logging.error(f"An error occurred during validation: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())