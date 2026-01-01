"""
Source Reference Tracker for Backend Multi-Agent System for Book RAG Chatbot

This module provides functionality to ensure all responses include proper citations
and source references as required by the specification.
"""
from typing import List, Dict, Any, Optional
from .models import AgentResponse, RetrievedContext
import logging

logger = logging.getLogger(__name__)

class SourceReferenceTracker:
    """
    Tracker for ensuring all responses include proper source references
    """

    def __init__(self):
        pass

    def extract_references_from_context(self, context: RetrievedContext) -> List[Dict[str, Any]]:
        """
        Extract source references from retrieved context

        Args:
            context: The retrieved context to extract references from

        Returns:
            List of source reference dictionaries
        """
        references = []

        for i, (passage, score, metadata) in enumerate(zip(
            context.passages,
            context.similarity_scores,
            context.source_metadata
        )):
            reference = {
                "passage": passage,
                "source": metadata.get("source", f"Section {i+1}"),
                "similarity_score": score,
                "metadata": metadata
            }
            references.append(reference)

        logger.info(f"Extracted {len(references)} references from context")
        return references

    def extract_references_from_selected_text(self, selected_text: str) -> List[Dict[str, Any]]:
        """
        Create source references for user-provided selected text

        Args:
            selected_text: The user-provided text to create references for

        Returns:
            List containing a single reference for the selected text
        """
        reference = {
            "passage": selected_text,
            "source": "user_selected_text",
            "similarity_score": 1.0,
            "metadata": {"type": "user_selection"}
        }

        logger.info("Created reference for user-selected text")
        return [reference]

    def validate_response_references(self, response: AgentResponse) -> bool:
        """
        Validate that the response contains proper source references

        Args:
            response: The AgentResponse to validate

        Returns:
            True if the response has valid references, False otherwise
        """
        if not response.source_references:
            logger.error("Response has no source references")
            return False

        # Check that each reference has required fields
        for i, ref in enumerate(response.source_references):
            required_fields = ["passage", "source"]
            for field in required_fields:
                if field not in ref:
                    logger.error(f"Reference {i} missing required field: {field}")
                    return False

        logger.info(f"Validated {len(response.source_references)} source references in response")
        return True

    def enhance_response_with_references(self, response: AgentResponse, context: RetrievedContext) -> AgentResponse:
        """
        Enhance a response by adding or updating source references from context

        Args:
            response: The AgentResponse to enhance
            context: The context to extract references from

        Returns:
            Enhanced AgentResponse with updated source references
        """
        # Extract references from context
        context_references = self.extract_references_from_context(context)

        # If the response already has references, combine them
        if response.source_references:
            # Add new references that aren't already in the response
            existing_passages = {ref["passage"] for ref in response.source_references}
            for ref in context_references:
                if ref["passage"] not in existing_passages:
                    response.source_references.append(ref)
        else:
            # Set the references from context
            response.source_references = context_references

        logger.info(f"Enhanced response with {len(response.source_references)} source references")
        return response

    def format_references_for_response(self, references: List[Dict[str, Any]], max_refs: int = 5) -> str:
        """
        Format references for inclusion in the response text

        Args:
            references: List of reference dictionaries
            max_refs: Maximum number of references to format

        Returns:
            Formatted string of references
        """
        if not references:
            return ""

        formatted_refs = []
        for i, ref in enumerate(references[:max_refs]):
            source = ref.get("source", f"Source {i+1}")
            passage = ref["passage"][:200] + "..." if len(ref["passage"]) > 200 else ref["passage"]  # Truncate long passages
            formatted_refs.append(f"[{i+1}] From {source}: {passage}")

        return "\n\n" + "\n\n".join(formatted_refs)

    def ensure_response_has_references(self, response: AgentResponse, context: RetrievedContext) -> AgentResponse:
        """
        Ensure that a response has proper source references, adding them if necessary

        Args:
            response: The AgentResponse to ensure has references
            context: The context to use for generating references

        Returns:
            AgentResponse with proper source references
        """
        if not response.source_references:
            # Extract references from context and add them to the response
            references = self.extract_references_from_context(context)
            response.source_references = references
            logger.info(f"Added {len(references)} references to response with no existing references")

        # Validate the references
        is_valid = self.validate_response_references(response)
        if not is_valid:
            logger.warning("Response references validation failed")

        return response

    def track_response_grounding(self, response_text: str, references: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Track how well the response is grounded in the provided references

        Args:
            response_text: The text of the response
            references: List of source references

        Returns:
            Dictionary with grounding metrics
        """
        response_words = set(response_text.lower().split())

        total_overlap = 0
        total_reference_words = 0

        for ref in references:
            ref_words = set(ref["passage"].lower().split())
            overlap = len(response_words.intersection(ref_words))
            total_overlap += overlap
            total_reference_words += len(ref_words)

        if total_reference_words == 0:
            grounding_score = 0.0
        else:
            grounding_score = total_overlap / total_reference_words

        # Additional metrics
        metrics = {
            "grounding_score": grounding_score,
            "total_overlap_words": total_overlap,
            "total_reference_words": total_reference_words,
            "reference_count": len(references)
        }

        logger.info(f"Grounding metrics: {metrics}")
        return metrics

    def create_citation_format(self, references: List[Dict[str, Any]]) -> str:
        """
        Create a proper citation format for the references

        Args:
            references: List of source references

        Returns:
            Formatted citation string
        """
        if not references:
            return ""

        citations = []
        for i, ref in enumerate(references):
            source = ref.get("source", f"Source {i+1}")
            similarity = ref.get("similarity_score", 0.0)
            citations.append(f"[{i+1}] {source} (similarity: {similarity:.2f})")

        return "References: " + "; ".join(citations)


# Global instance for easy access
source_reference_tracker = SourceReferenceTracker()