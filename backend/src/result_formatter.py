from typing import List, Dict, Any
import logging


def format_retrieved_results(results: List[Dict[str, Any]]) -> str:
    """
    Format retrieved results for display with score, text preview, and source.

    Args:
        results: List of retrieved chunks with scores and payloads

    Returns:
        Formatted string representation of the results
    """
    if not results:
        return "No results retrieved."

    formatted_output = []
    formatted_output.append("Retrieved Results:")
    formatted_output.append("=" * 50)

    for i, result in enumerate(results, 1):
        score = result.get('score', 0)
        payload = result.get('payload', {})

        # Extract fields with defaults
        text_content = payload.get('text', '')
        source = payload.get('source', 'Unknown')
        text_preview = text_content[:200] if text_content else 'No text content'

        formatted_output.append(f"Result {i}:")
        formatted_output.append(f"  Score: {score:.4f}")
        formatted_output.append(f"  Source: {source}")
        formatted_output.append(f"  Text Preview: {text_preview}...")
        if len(text_content) > 200:
            formatted_output.append(f"  Full Text: {text_content}")
        formatted_output.append("  " + "-" * 30)

    return "\n".join(formatted_output)


def print_retrieved_results(results: List[Dict[str, Any]]) -> None:
    """
    Print retrieved results in the required format: score, text preview, and source.

    Args:
        results: List of retrieved chunks with scores and payloads
    """
    if not results:
        logging.info("No results retrieved.")
        return

    logging.info("Retrieved Results:")
    for i, result in enumerate(results, 1):
        score = result.get('score', 0)
        payload = result.get('payload', {})

        # Extract fields with defaults
        text_content = payload.get('text', '')
        source = payload.get('source', 'Unknown')
        text_preview = text_content[:200] if text_content else 'No text content'

        print(f"Score: {score:.4f}")
        print(f"Source: {source}")
        print(f"Text Preview: {text_preview}...")
        if len(text_content) > 200:
            print(f"Full Text: {text_content}")
        print("---")