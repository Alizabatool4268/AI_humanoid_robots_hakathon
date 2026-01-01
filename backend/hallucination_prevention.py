"""
Hallucination Prevention for Backend Multi-Agent System for Book RAG Chatbot

This module implements mechanisms to prevent hallucinations by validating that
all responses are grounded in the provided or retrieved text.
"""
from typing import List, Dict, Any, Tuple
from .models import AgentResponse, RetrievedContext
from .validators import api_response_validator
import logging
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class HallucinationPreventionService:
    """
    Service for preventing hallucinations in generated responses
    """

    def __init__(self):
        self.validator = api_response_validator

    def validate_response_against_context(self, response: AgentResponse, context: RetrievedContext) -> Tuple[bool, List[str]]:
        """
        Validate that the response is grounded in the provided context

        Args:
            response: The AgentResponse to validate
            context: The context used to generate the response

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        if not context.passages:
            # If no context was provided, check if response indicates this appropriately
            if "no relevant content found" in response.answer.lower():
                return True, []
            else:
                issues.append("Response claims to have information when no context was provided")
                return False, issues

        # Combine all context passages into one text for comparison
        context_text = " ".join(context.passages).lower()
        response_text = response.answer.lower()

        # Check if response contains information that's not in context
        response_sentences = self._split_into_sentences(response_text)
        context_sentences = self._split_into_sentences(context_text)

        non_grounded_sentences = []
        for sentence in response_sentences:
            if not self._sentence_is_grounded(sentence, context_sentences):
                non_grounded_sentences.append(sentence)

        if non_grounded_sentences:
            issues.append(f"Found {len(non_grounded_sentences)} sentences that may not be grounded in context")
            logger.warning(f"Potential hallucinations detected: {non_grounded_sentences}")

        # Check for factual claims that contradict context
        contradictions = self._find_contradictions(response_text, context_text)
        if contradictions:
            issues.extend(contradictions)
            logger.warning(f"Potential contradictions detected: {contradictions}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def validate_response_against_selected_text(self, response: AgentResponse, selected_text: str) -> Tuple[bool, List[str]]:
        """
        Validate that the response is grounded in the user-provided selected text

        Args:
            response: The AgentResponse to validate
            selected_text: The selected text used as context

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check if response contains information that's not in selected text
        selected_text_lower = selected_text.lower()
        response_text = response.answer.lower()

        response_sentences = self._split_into_sentences(response_text)
        selected_sentences = self._split_into_sentences(selected_text_lower)

        non_grounded_sentences = []
        for sentence in response_sentences:
            if not self._sentence_is_grounded(sentence, selected_sentences):
                non_grounded_sentences.append(sentence)

        if non_grounded_sentences:
            issues.append(f"Found {len(non_grounded_sentences)} sentences that may not be grounded in selected text")
            logger.warning(f"Potential hallucinations in selected text response: {non_grounded_sentences}")

        # Check for contradictions with selected text
        contradictions = self._find_contradictions(response_text, selected_text_lower)
        if contradictions:
            issues.extend(contradictions)
            logger.warning(f"Potential contradictions with selected text: {contradictions}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for analysis

        Args:
            text: The text to split

        Returns:
            List of sentences
        """
        # Split text into sentences using common sentence delimiters
        sentences = re.split(r'[.!?]+', text)
        # Remove empty strings and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _sentence_is_grounded(self, sentence: str, context_sentences: List[str], threshold: float = 0.3) -> bool:
        """
        Check if a sentence is grounded in the context sentences

        Args:
            sentence: The sentence to check
            context_sentences: List of context sentences
            threshold: Similarity threshold for grounding

        Returns:
            True if sentence is grounded, False otherwise
        """
        if not sentence.strip():
            return True  # Empty sentence is trivially grounded

        # Check for direct matches or high similarity
        for context_sentence in context_sentences:
            similarity = SequenceMatcher(None, sentence.lower(), context_sentence.lower()).ratio()
            if similarity >= threshold:
                return True

        # Check for semantic overlap using word matching
        sentence_words = set(sentence.lower().split())
        if not sentence_words:
            return True

        for context_sentence in context_sentences:
            context_words = set(context_sentence.lower().split())
            if not context_words:
                continue

            # Calculate overlap ratio
            common_words = sentence_words.intersection(context_words)
            overlap_ratio = len(common_words) / len(sentence_words)

            if overlap_ratio >= threshold:
                return True

        return False

    def _find_contradictions(self, response_text: str, context_text: str) -> List[str]:
        """
        Find potential contradictions between response and context

        Args:
            response_text: The response text
            context_text: The context text

        Returns:
            List of potential contradictions
        """
        contradictions = []

        # Look for specific contradiction patterns
        response_lower = response_text.lower()
        context_lower = context_text.lower()

        # Check for negation patterns that might contradict context
        negation_patterns = [
            (r"not\s+(\w+)", r"\1"),  # "not X" vs "X"
            (r"never\s+(\w+)", r"\1"),  # "never X" vs "X"
            (r"no\s+(\w+)", r"\1"),  # "no X" vs "X"
        ]

        for neg_pattern, pos_pattern in negation_patterns:
            neg_matches = re.findall(neg_pattern, response_lower)
            pos_matches = re.findall(pos_pattern, context_lower)

            for neg_match in neg_matches:
                if neg_match in pos_matches:
                    contradictions.append(f"Potential contradiction: response says 'not {neg_match}' but context says '{neg_match}'")

        return contradictions

    def filter_response_for_hallucinations(self, response: AgentResponse, context: RetrievedContext) -> AgentResponse:
        """
        Filter a response to remove potential hallucinations

        Args:
            response: The original AgentResponse
            context: The context used to generate the response

        Returns:
            Filtered AgentResponse with potential hallucinations removed
        """
        if not context.passages:
            return response

        context_text = " ".join(context.passages).lower()
        response_sentences = self._split_into_sentences(response.answer)

        grounded_sentences = []
        for sentence in response_sentences:
            if self._sentence_is_grounded(sentence.lower(), [ctx.lower() for ctx in context.passages]):
                grounded_sentences.append(sentence)

        if not grounded_sentences:
            # If no sentences are grounded, return a safe response
            filtered_answer = "No relevant content found in the provided context."
            logger.warning("All sentences in response were filtered out due to potential hallucinations")
        else:
            filtered_answer = " ".join(grounded_sentences)

        # Create new response with filtered answer
        filtered_response = AgentResponse(
            answer=filtered_answer,
            source_references=response.source_references,
            confidence_score=max(0.0, response.confidence_score - 0.2),  # Reduce confidence due to filtering
            processing_time=response.processing_time,
            was_handoff=response.was_handoff
        )

        logger.info(f"Filtered response from {len(response_sentences)} to {len(grounded_sentences)} sentences")
        return filtered_response

    def validate_and_correct_response(self, response: AgentResponse, context: RetrievedContext) -> Tuple[AgentResponse, bool]:
        """
        Validate response for hallucinations and return corrected version if needed

        Args:
            response: The original AgentResponse
            context: The context used to generate the response

        Returns:
            Tuple of (corrected_response, was_corrected)
        """
        is_valid, issues = self.validate_response_against_context(response, context)

        if is_valid:
            return response, False

        # If invalid, try to filter the response
        corrected_response = self.filter_response_for_hallucinations(response, context)
        is_corrected_valid, _ = self.validate_response_against_context(corrected_response, context)

        if is_corrected_valid:
            logger.info("Response corrected to remove hallucinations")
            return corrected_response, True
        else:
            # If filtering didn't work, return a safe response
            safe_response = AgentResponse(
                answer="No relevant content found in the provided context.",
                source_references=[],
                confidence_score=0.0,
                processing_time=response.processing_time,
                was_handoff=response.was_handoff
            )
            logger.warning("Response could not be corrected, returning safe response")
            return safe_response, True

    def validate_response_grounding(self, response: AgentResponse, source_content: str) -> bool:
        """
        Validate that the response is grounded in the source content

        Args:
            response: The AgentResponse to validate
            source_content: The source content to validate against

        Returns:
            True if response is grounded, False otherwise
        """
        try:
            # Use the existing validator as a base
            is_basic_valid = self.validator.validate_grounding(response, source_content)
            if not is_basic_valid:
                return False

            # Perform additional hallucination checks
            response_sentences = self._split_into_sentences(response.answer)
            source_sentences = self._split_into_sentences(source_content)

            # Check each sentence for grounding
            ungrounded_count = 0
            for sentence in response_sentences:
                if not self._sentence_is_grounded(sentence.lower(), [s.lower() for s in source_sentences]):
                    ungrounded_count += 1

            # Consider hallucinated if more than 30% of sentences are ungrounded
            if len(response_sentences) > 0:
                ungrounded_ratio = ungrounded_count / len(response_sentences)
                return ungrounded_ratio <= 0.3

            return True

        except Exception as e:
            logger.error(f"Error during grounding validation: {str(e)}")
            return False


# Global instance for easy access
hallucination_prevention_service = HallucinationPreventionService()