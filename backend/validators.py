"""
API Response Validators for Backend Multi-Agent System for Book RAG Chatbot

This module provides validation functions to ensure responses meet grounding requirements
and follow the proper format as specified in the contracts.
"""
from typing import Dict, Any, List, Optional
from models import AgentResponse, RetrievedContext, UserQuery
import logging

logger = logging.getLogger(__name__)

class APIResponseValidator:
    """
    Validator class for ensuring API responses meet grounding requirements
    """

    @staticmethod
    def validate_agent_response(response: AgentResponse) -> bool:
        """
        Validate that the agent response meets all requirements:
        - Answer is grounded in provided or retrieved text
        - Source references are present
        - Confidence score is within range
        - All requirements from the specification are met

        Args:
            response: The AgentResponse to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check that source_references is not empty when answer is provided
            if not response.source_references:
                logger.error("Validation failed: source_references is empty")
                return False

            # Check that confidence score is between 0.0 and 1.0
            if not 0.0 <= response.confidence_score <= 1.0:
                logger.error(f"Validation failed: confidence_score {response.confidence_score} is out of range")
                return False

            # Check that answer is not empty
            if not response.answer or not response.answer.strip():
                logger.error("Validation failed: answer is empty")
                return False

            # All validations passed
            logger.info("AgentResponse validation passed")
            return True

        except Exception as e:
            logger.error(f"Error during response validation: {str(e)}")
            return False

    @staticmethod
    def validate_retrieved_context(context: RetrievedContext) -> bool:
        """
        Validate that the retrieved context meets requirements:
        - Passages are present when using vector search
        - Similarity scores match passage count
        - All passages are from original book content

        Args:
            context: The RetrievedContext to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if retrieval method is vector search and passages are present
            if context.retrieval_method == "vector_search" and not context.passages:
                logger.error("Validation failed: passages array is empty for vector_search method")
                return False

            # Check that similarity scores match passage count
            if len(context.similarity_scores) != len(context.passages):
                logger.error(f"Validation failed: similarity_scores count ({len(context.similarity_scores)}) "
                           f"doesn't match passages count ({len(context.passages)})")
                return False

            # Check that similarity scores are within range
            for score in context.similarity_scores:
                if not 0.0 <= score <= 1.0:
                    logger.error(f"Validation failed: similarity_score {score} is out of range")
                    return False

            # All validations passed
            logger.info("RetrievedContext validation passed")
            return True

        except Exception as e:
            logger.error(f"Error during context validation: {str(e)}")
            return False

    @staticmethod
    def validate_user_query(query: UserQuery) -> bool:
        """
        Validate that the user query meets requirements:
        - Query text is not empty
        - Selected text is meaningful if provided

        Args:
            query: The UserQuery to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check that query_text is not empty
            if not query.query_text or not query.query_text.strip():
                logger.error("Validation failed: query_text is empty")
                return False

            # Check that selected_text is meaningful if provided
            if query.selected_text and len(query.selected_text.strip()) < 10:
                logger.error("Validation failed: selected_text is less than 10 characters")
                return False

            # All validations passed
            logger.info("UserQuery validation passed")
            return True

        except Exception as e:
            logger.error(f"Error during query validation: {str(e)}")
            return False

    @staticmethod
    def validate_grounding(response: AgentResponse, source_content: str) -> bool:
        """
        Validate that the response is grounded in the provided source content.

        Args:
            response: The AgentResponse to validate for grounding
            source_content: The source content that should be referenced

        Returns:
            True if the response is grounded in the source, False otherwise
        """
        try:
            # Check if the response content appears to be based on the source
            # This is a simple check - in a real implementation, more sophisticated
            # NLP techniques would be used to validate grounding
            response_lower = response.answer.lower()
            source_lower = source_content.lower()

            # Check if there are common terms between response and source
            response_words = set(response_lower.split())
            source_words = set(source_lower.split())
            common_words = response_words.intersection(source_words)

            # If less than 30% of response words appear in source, consider not grounded
            if len(response_words) == 0:
                return False

            overlap_ratio = len(common_words) / len(response_words)
            is_valid = overlap_ratio > 0.3

            if not is_valid:
                logger.error(f"Response grounding validation failed: {overlap_ratio:.2%} overlap with source")
                return False

            logger.info(f"Response grounding validation passed: {overlap_ratio:.2%} overlap with source")
            return True

        except Exception as e:
            logger.error(f"Error during grounding validation: {str(e)}")
            return False

    @staticmethod
    def validate_selected_text_response(response: AgentResponse, selected_text: str) -> bool:
        """
        Validate that a response based on selected text meets requirements:
        - Contains proper source references
        - Is grounded in the selected text
        - Confidence score is appropriate

        Args:
            response: The AgentResponse to validate
            selected_text: The selected text used as context

        Returns:
            True if the response is valid, False otherwise
        """
        try:
            # Validate basic response structure
            if not self.validate_agent_response(response):
                logger.error("Selected text response failed basic validation")
                return False

            # Validate that source references point to the selected text
            if not response.source_references:
                logger.error("Selected text response has no source references")
                return False

            # Check that at least one reference points to the selected text
            selected_text_ref_found = False
            for ref in response.source_references:
                if ref.get("source") == "user_selected_text" or "selected_text" in ref.get("source", ""):
                    selected_text_ref_found = True
                    break

            if not selected_text_ref_found:
                logger.error("No source reference points to user selected text")
                return False

            # Validate grounding in selected text
            is_grounded = self.validate_grounding(response, selected_text)
            if not is_grounded:
                logger.error("Response is not properly grounded in selected text")
                return False

            # For selected text responses, confidence should be high
            if response.confidence_score < 0.7:
                logger.warning(f"Selected text response has low confidence: {response.confidence_score}")

            logger.info("Selected text response validation passed")
            return True

        except Exception as e:
            logger.error(f"Error during selected text response validation: {str(e)}")
            return False

    @staticmethod
    def validate_response_format(response_data: Dict[str, Any]) -> bool:
        """
        Validate that the API response format matches the contract specification.

        Args:
            response_data: The response data dictionary to validate

        Returns:
            True if format is valid, False otherwise
        """
        try:
            required_fields = ["answer", "source_references", "confidence_score", "processing_time", "was_handoff"]

            for field in required_fields:
                if field not in response_data:
                    logger.error(f"Validation failed: required field '{field}' missing from response")
                    return False

            # Validate specific field types and constraints
            if not isinstance(response_data["answer"], str):
                logger.error("Validation failed: 'answer' field is not a string")
                return False

            if not isinstance(response_data["source_references"], list):
                logger.error("Validation failed: 'source_references' field is not a list")
                return False

            if not isinstance(response_data["confidence_score"], (int, float)) or not 0.0 <= response_data["confidence_score"] <= 1.0:
                logger.error("Validation failed: 'confidence_score' is not a number between 0.0 and 1.0")
                return False

            if not isinstance(response_data["processing_time"], (int, float)) or response_data["processing_time"] < 0:
                logger.error("Validation failed: 'processing_time' is not a non-negative number")
                return False

            if not isinstance(response_data["was_handoff"], bool):
                logger.error("Validation failed: 'was_handoff' is not a boolean")
                return False

            # All validations passed
            logger.info("Response format validation passed")
            return True

        except Exception as e:
            logger.error(f"Error during format validation: {str(e)}")
            return False


# Global instance for easy access
api_response_validator = APIResponseValidator()