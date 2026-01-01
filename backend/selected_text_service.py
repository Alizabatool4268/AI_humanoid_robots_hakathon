"""
Selected Text Processing Service for Backend Multi-Agent System for Book RAG Chatbot

This module provides functionality to process user-provided selected text
that should override general retrieval.
"""
from typing import Dict, Any, List
from .models import RetrievedContext
import logging

logger = logging.getLogger(__name__)

class SelectedTextService:
    """
    Service for processing user-provided selected text that overrides general retrieval
    """

    def __init__(self):
        pass

    def process_selected_text(self, selected_text: str, query: str = "") -> RetrievedContext:
        """
        Process the user-provided selected text to create a RetrievedContext

        Args:
            selected_text: The text provided by the user that should override retrieval
            query: The original query (for context, though not used directly)

        Returns:
            RetrievedContext with the selected text as the primary source
        """
        if not selected_text or not selected_text.strip():
            raise ValueError("Selected text cannot be empty")

        # Create a RetrievedContext with the selected text as the primary source
        retrieved_context = RetrievedContext(
            passages=[selected_text],
            similarity_scores=[1.0],  # Perfect similarity since it's the exact provided text
            source_metadata=[{
                "source": "user_selected_text",
                "type": "user_input",
                "original_query": query[:100] if query else ""  # Store truncated query for reference
            }],
            retrieval_method="selected_text"
        )

        logger.info(f"Processed selected text of length {len(selected_text)} characters")
        return retrieved_context

    def validate_selected_text(self, selected_text: str) -> bool:
        """
        Validate that the selected text meets requirements

        Args:
            selected_text: The text to validate

        Returns:
            True if valid, False otherwise
        """
        if not selected_text:
            logger.error("Selected text is empty")
            return False

        if len(selected_text.strip()) < 10:
            logger.error(f"Selected text is too short: {len(selected_text)} characters")
            return False

        # Additional validation could be added here (e.g., check for valid content)
        logger.info("Selected text validation passed")
        return True

    def preprocess_selected_text(self, selected_text: str) -> str:
        """
        Preprocess the selected text (clean, normalize, etc.)

        Args:
            selected_text: The raw selected text

        Returns:
            Preprocessed selected text
        """
        # Basic preprocessing: strip whitespace and normalize line breaks
        processed_text = selected_text.strip()
        # Replace multiple newlines with a single newline
        import re
        processed_text = re.sub(r'\n\s*\n', '\n\n', processed_text)
        # Replace tabs with spaces
        processed_text = processed_text.replace('\t', '  ')

        logger.info(f"Preprocessed selected text from {len(selected_text)} to {len(processed_text)} characters")
        return processed_text

    def create_context_from_multiple_selections(self, selected_texts: List[str], query: str = "") -> RetrievedContext:
        """
        Create a RetrievedContext from multiple selected text passages

        Args:
            selected_texts: List of selected text passages
            query: The original query (for context)

        Returns:
            RetrievedContext combining all selected texts
        """
        if not selected_texts:
            raise ValueError("Selected texts list cannot be empty")

        # Validate each selected text
        valid_texts = []
        for i, text in enumerate(selected_texts):
            if self.validate_selected_text(text):
                valid_texts.append(self.preprocess_selected_text(text))
            else:
                logger.warning(f"Skipping invalid selected text at index {i}")

        if not valid_texts:
            raise ValueError("No valid selected texts after validation")

        # Create a RetrievedContext with all valid texts
        retrieved_context = RetrievedContext(
            passages=valid_texts,
            similarity_scores=[1.0] * len(valid_texts),  # All have perfect similarity
            source_metadata=[{
                "source": f"user_selected_text_{i+1}",
                "type": "user_input",
                "index": i,
                "original_query": query[:100] if query else ""
            } for i in range(len(valid_texts))],
            retrieval_method="selected_text"
        )

        logger.info(f"Created context from {len(valid_texts)} selected text passages")
        return retrieved_context

    def extract_key_phrases(self, selected_text: str, max_phrases: int = 10) -> List[str]:
        """
        Extract key phrases from selected text for better matching

        Args:
            selected_text: The selected text to analyze
            max_phrases: Maximum number of phrases to extract

        Returns:
            List of key phrases from the selected text
        """
        # Simple approach: split by sentences and take the most substantial ones
        import re
        sentences = re.split(r'[.!?]+', selected_text)
        # Filter out short sentences and clean them
        key_phrases = []
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 20:  # Only include substantial sentences
                key_phrases.append(clean_sentence)

        # Limit to max_phrases
        key_phrases = key_phrases[:max_phrases]

        logger.info(f"Extracted {len(key_phrases)} key phrases from selected text")
        return key_phrases

    def get_text_summary(self, selected_text: str, max_length: int = 200) -> str:
        """
        Get a summary of the selected text (truncated version)

        Args:
            selected_text: The selected text to summarize
            max_length: Maximum length of the summary

        Returns:
            Truncated summary of the selected text
        """
        if len(selected_text) <= max_length:
            return selected_text

        # Truncate and add ellipsis
        truncated = selected_text[:max_length].rsplit(' ', 1)[0] + "..."
        logger.info(f"Text truncated from {len(selected_text)} to {len(truncated)} characters")
        return truncated


# Global instance for easy access
selected_text_service = SelectedTextService()