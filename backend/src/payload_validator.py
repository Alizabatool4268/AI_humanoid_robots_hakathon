from typing import List, Dict, Any
import logging


def validate_payload_structure(payload: Dict[str, Any]) -> bool:
    """
    Validate that the payload contains the required 'text' and 'source' fields.

    Args:
        payload: The payload dictionary to validate

    Returns:
        True if payload has required fields, False otherwise
    """
    required_fields = ['text', 'source']

    for field in required_fields:
        if field not in payload:
            logging.error(f"Missing required field '{field}' in payload")
            return False

        if payload[field] is None:
            logging.error(f"Required field '{field}' is None in payload")
            return False

        if field == 'text' and not isinstance(payload[field], str):
            logging.error(f"Required field '{field}' is not a string in payload")
            return False

        if field == 'source' and not isinstance(payload[field], str):
            logging.error(f"Required field '{field}' is not a string in payload")
            return False

    return True


def validate_retrieved_payloads(results: List[Dict[str, Any]]) -> bool:
    """
    Validate that all retrieved results have payloads with required fields.

    Args:
        results: List of retrieved chunks with scores and payloads

    Returns:
        True if all payloads are valid, False otherwise
    """
    if not results:
        logging.warning("No results to validate")
        return False

    all_valid = True
    for i, result in enumerate(results):
        payload = result.get('payload', {})

        if not payload:
            logging.error(f"Result {i+1} has empty or missing payload")
            all_valid = False
            continue

        if not validate_payload_structure(payload):
            logging.error(f"Result {i+1} has invalid payload structure")
            all_valid = False
        else:
            # Log successful validation for each result
            text_preview = payload.get('text', '')[:100]  # First 100 chars as preview
            logging.debug(f"Result {i+1} payload validated successfully: {text_preview}...")

    if all_valid:
        logging.info(f"All {len(results)} retrieved payloads have valid structure with required 'text' and 'source' fields")
    else:
        logging.error("Some retrieved payloads have invalid structure")

    return all_valid