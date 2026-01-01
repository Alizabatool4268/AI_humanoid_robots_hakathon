"""
Response Generation Service for Backend Multi-Agent System for Book RAG Chatbot

This module provides grounded response generation using the Gemini model.
"""
from typing import List, Dict, Any
from gemini_service import gemini_service
from models import RetrievedContext, AgentResponse
from validators import api_response_validator
import logging
import time

logger = logging.getLogger(__name__)

class ResponseGenerationService:
    """
    Service for generating grounded responses using Gemini based on context
    """

    def __init__(self):
        self.gemini_service = gemini_service

    def generate_response(self, context: RetrievedContext, query: str) -> AgentResponse:
        """
        Generate a response based on the provided context and query

        Args:
            context: The retrieved context to use for generating the response
            query: The user's query

        Returns:
            AgentResponse containing the generated answer and metadata
        """
        start_time = time.time()

        # Combine context passages into a single context string
        if not context.passages:
            # If no context passages, return a response indicating this
            answer = "No relevant content found"
            source_references = []
            confidence_score = 0.0
        else:
            # Combine passages with metadata to create full context
            context_parts = []
            source_references = []

            for i, (passage, score, metadata) in enumerate(zip(
                context.passages,
                context.similarity_scores,
                context.source_metadata
            )):
                context_parts.append(f"Passage {i+1}: {passage}")
                source_references.append({
                    "passage": passage,
                    "source": metadata.get("source", f"Section {i+1}"),
                    "similarity_score": score
                })

            full_context = "\n\n".join(context_parts)

            # Generate response using Gemini
            answer = self.gemini_service.generate_response(full_context, query)

            # Calculate confidence based on similarity scores
            if context.similarity_scores:
                avg_similarity = sum(context.similarity_scores) / len(context.similarity_scores)
                # Normalize confidence based on average similarity
                confidence_score = min(1.0, avg_similarity * 2)  # Scale up since similarity scores might be low
            else:
                confidence_score = 0.5  # Default confidence when no similarity scores

        # Calculate processing time
        processing_time = time.time() - start_time

        # Create AgentResponse
        agent_response = AgentResponse(
            answer=answer,
            source_references=source_references,
            confidence_score=confidence_score,
            processing_time=processing_time,
            was_handoff=False  # This will be set by the agent system if applicable
        )

        # Validate the response
        is_valid = api_response_validator.validate_agent_response(agent_response)
        if not is_valid:
            logger.warning("Generated response did not pass validation")

        # Validate grounding
        if context.passages:
            context_text = " ".join(context.passages)
            is_grounded = api_response_validator.validate_grounding(agent_response, context_text)
            if not is_grounded:
                logger.warning("Generated response may not be properly grounded in context")

        logger.info(f"Generated response for query '{query[:50]}...' in {processing_time:.4f}s with confidence {confidence_score:.2f}")
        return agent_response

    def generate_response_with_selected_text(self, selected_text: str, query: str) -> AgentResponse:
        """
        Generate a response using selected text as the primary context

        Args:
            selected_text: The user-provided text to use as context
            query: The user's query

        Returns:
            AgentResponse containing the generated answer and metadata
        """
        start_time = time.time()

        # Use selected text as the context
        answer = self.gemini_service.generate_response(selected_text, query)

        # Create source references for selected text
        source_references = [{
            "passage": selected_text,
            "source": "user_selected_text",
            "similarity_score": 1.0  # Perfect match since this is the exact provided text
        }]

        # Calculate confidence (high confidence since this is the exact provided context)
        confidence_score = 0.9

        # Calculate processing time
        processing_time = time.time() - start_time

        # Create AgentResponse
        agent_response = AgentResponse(
            answer=answer,
            source_references=source_references,
            confidence_score=confidence_score,
            processing_time=processing_time,
            was_handoff=False  # This will be set by the agent system if applicable
        )

        # Validate the response
        is_valid = api_response_validator.validate_agent_response(agent_response)
        if not is_valid:
            logger.warning("Generated response with selected text did not pass validation")

        # Validate grounding
        is_grounded = api_response_validator.validate_grounding(agent_response, selected_text)
        if not is_grounded:
            logger.warning("Generated response with selected text may not be properly grounded")

        logger.info(f"Generated response with selected text for query '{query[:50]}...' in {processing_time:.4f}s")
        return agent_response

    def generate_response_with_primary_context(self, primary_context: str, fallback_context: RetrievedContext = None, query: str = "") -> AgentResponse:
        """
        Generate a response prioritizing primary context (like selected text) over fallback context

        Args:
            primary_context: The primary context to use (e.g., selected text)
            fallback_context: Optional fallback context if primary is insufficient
            query: The user's query

        Returns:
            AgentResponse containing the generated answer and metadata
        """
        start_time = time.time()

        # Use primary context first
        answer = self.gemini_service.generate_response(primary_context, query)

        # Create source references for primary context
        source_references = [{
            "passage": primary_context,
            "source": "primary_context",
            "similarity_score": 1.0
        }]

        # If fallback context is provided and the primary context is insufficient,
        # we might want to incorporate it, but for now we prioritize the primary
        confidence_score = 0.9  # High confidence for primary context

        # Calculate processing time
        processing_time = time.time() - start_time

        # Create AgentResponse
        agent_response = AgentResponse(
            answer=answer,
            source_references=source_references,
            confidence_score=confidence_score,
            processing_time=processing_time,
            was_handoff=False
        )

        # Validate the response
        is_valid = api_response_validator.validate_agent_response(agent_response)
        if not is_valid:
            logger.warning("Generated response with primary context did not pass validation")

        # Validate grounding
        is_grounded = api_response_validator.validate_grounding(agent_response, primary_context)
        if not is_grounded:
            logger.warning("Generated response with primary context may not be properly grounded")

        logger.info(f"Generated response with primary context for query '{query[:50]}...' in {processing_time:.4f}s")
        return agent_response

    def generate_summarized_response(self, context: RetrievedContext, query: str) -> AgentResponse:
        """
        Generate a summarized response that combines information from multiple passages

        Args:
            context: The retrieved context to use for generating the response
            query: The user's query

        Returns:
            AgentResponse containing the generated summary answer and metadata
        """
        if not context.passages:
            # If no context, return a response indicating this
            return self.generate_response(context, query)

        start_time = time.time()

        # Create a prompt that asks for a summary combining information from multiple passages
        passages_with_sources = []
        source_references = []

        for i, (passage, score, metadata) in enumerate(zip(
            context.passages,
            context.similarity_scores,
            context.source_metadata
        )):
            passage_with_source = f"Source {i+1} ({metadata.get('source', 'Unknown')}): {passage}"
            passages_with_sources.append(passage_with_source)
            source_references.append({
                "passage": passage,
                "source": metadata.get("source", f"Section {i+1}"),
                "similarity_score": score
            })

        full_context = "\n\n".join(passages_with_sources)

        # Create a specific prompt for summarization
        prompt = f"""
        Based on the following sources, provide a comprehensive answer to the query.
        Synthesize information from multiple sources where relevant.
        Only use information from the provided sources.
        If the sources don't contain information to answer the query, respond with "No relevant content found".

        Sources:
        {full_context}

        Query: {query}

        Answer (combine information from multiple sources as needed):
        """

        # For this implementation, we'll use the standard generate_response method
        # In a real implementation, we might have a more sophisticated summarization approach
        answer = self.gemini_service.generate_response(full_context, query)

        # Calculate confidence based on average similarity
        avg_similarity = sum(context.similarity_scores) / len(context.similarity_scores) if context.similarity_scores else 0.5
        confidence_score = min(1.0, avg_similarity * 2)

        # Calculate processing time
        processing_time = time.time() - start_time

        # Create AgentResponse
        agent_response = AgentResponse(
            answer=answer,
            source_references=source_references,
            confidence_score=confidence_score,
            processing_time=processing_time,
            was_handoff=False
        )

        logger.info(f"Generated summarized response for query '{query[:50]}...' in {processing_time:.4f}s")
        return agent_response

    def validate_and_improve_response(self, context: RetrievedContext, query: str,
                                     max_attempts: int = 3) -> AgentResponse:
        """
        Generate a response and validate it, making multiple attempts if needed

        Args:
            context: The retrieved context to use for generating the response
            query: The user's query
            max_attempts: Maximum number of generation attempts

        Returns:
            A validated AgentResponse
        """
        for attempt in range(max_attempts):
            response = self.generate_response(context, query)

            # Check if response is valid and grounded
            is_valid = api_response_validator.validate_agent_response(response)
            if context.passages:
                context_text = " ".join(context.passages)
                is_grounded = api_response_validator.validate_grounding(response, context_text)
            else:
                is_grounded = True  # No context means no grounding validation needed

            if is_valid and is_grounded:
                logger.info(f"Generated valid and grounded response on attempt {attempt + 1}")
                return response
            else:
                logger.warning(f"Response failed validation on attempt {attempt + 1}, retrying...")

        logger.warning(f"Could not generate valid response after {max_attempts} attempts")
        # Return the last attempt even if it didn't pass validation
        return response


# Global instance for easy access
response_generation_service = ResponseGenerationService()