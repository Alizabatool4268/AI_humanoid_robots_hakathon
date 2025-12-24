#!/usr/bin/env python3
"""
Test script to retrieve any data from Qdrant to confirm the collection has content.
"""

import sys
import os
# Add the backend/src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging
from typing import List, Dict, Any


def main():
    """
    Main function to test Qdrant retrieval with a general query.
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

        # Phase 2: Test with a more general query to see if there's any content
        logging.info("Starting retrieval validation with a general query: 'AI'")

        # Try with a more general query
        results = retrieve_chunks(
            query="AI",
            result_limit=5,
            min_results=1  # Lower minimum since we're testing if ANY content exists
        )

        # Validate that we got results
        result_count = len(results)
        logging.info(f"Retrieved {result_count} chunks for the general query 'AI'")

        if result_count > 0:
            logging.info(f"✓ Successfully retrieved {result_count} relevant chunks")

            # Validate payload structure only if there are results
            if results:
                payload_validation_success = validate_retrieved_payloads(results)
                if payload_validation_success:
                    logging.info("✓ All retrieved payloads have valid structure with required 'text' and 'source' fields")
                    # Display the results using the formatter
                    print("Displaying retrieved results:")
                    print_retrieved_results(results)
                else:
                    logging.error("Payload validation failed. Some results are missing required 'text' or 'source' fields.")
        else:
            logging.warning("⚠ No results found even for the general query 'AI'")
            logging.info("This confirms the collection may not have content related to AI topics.")

        logging.info("General retrieval test completed.")
        return 0

    except ValueError as e:
        # Handle missing environment variables or validation errors
        logging.error(f"Configuration or validation error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        # Handle other errors
        logging.error(f"An error occurred during validation: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())