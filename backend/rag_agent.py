"""
Core RAG Pipeline for Backend Multi-Agent System for Book RAG Chatbot

This module implements the core RAG pipeline that connects search and generation.
"""
from typing import Optional, Dict, Any
from search_service import vector_search_service
from response_generator import response_generation_service
from models import UserQuery, RetrievedContext, AgentResponse, AgentState, AgentType
from validators import api_response_validator
from utils import log_execution_time, AgentLogger
import logging
import time

logger = logging.getLogger(__name__)
agent_logger = AgentLogger(__name__)

class RAGPipeline:
    """
    Core RAG pipeline that connects search and generation components
    """

    def __init__(self):
        self.search_service = vector_search_service
        self.response_generator = response_generation_service
        self.validator = api_response_validator

    @log_execution_time
    def process_query(self, user_query: UserQuery) -> AgentResponse:
        """
        Process a user query through the RAG pipeline

        Args:
            user_query: The user's query with optional selected text

        Returns:
            AgentResponse containing the answer and metadata
        """
        query_id = f"query_{int(time.time() * 1000)}"
        agent_logger.log_query_processing(query_id, user_query.query_text, "RAG")

        start_time = time.time()

        # Check if selected text is provided (it should override retrieval)
        if user_query.has_selected_text():
            agent_logger.log_retrieval_result(query_id, 1, "selected_text")
            # Use selected text as context instead of performing retrieval
            response = self.response_generator.generate_response_with_selected_text(
                user_query.selected_text,
                user_query.query_text
            )
        else:
            # Perform vector search to retrieve relevant context
            retrieved_context = self.search_service.search_by_text(
                user_query.query_text,
                limit=5  # Retrieve top 5 most similar passages
            )

            agent_logger.log_retrieval_result(query_id, len(retrieved_context.passages), "vector_search")

            # Generate response based on retrieved context
            response = self.response_generator.generate_response(
                retrieved_context,
                user_query.query_text
            )

        # Update processing time
        response.processing_time = time.time() - start_time

        # Validate the response
        is_valid = self.validator.validate_agent_response(response)
        agent_logger.log_validation_result(query_id, is_valid, "response_validation")

        if not is_valid:
            # If validation fails, create a default response
            logger.warning(f"Response validation failed for query {query_id}, creating default response")
            response = AgentResponse(
                answer="I couldn't generate a proper response. Please try rephrasing your question.",
                source_references=[],
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                was_handoff=False
            )

        agent_logger.log_response_generation(
            query_id,
            len(response.answer),
            response.confidence_score
        )

        return response

    def process_query_with_priority_handling(self, user_query: UserQuery) -> AgentResponse:
        """
        Process a user query with explicit priority handling for selected text

        Args:
            user_query: The user's query with optional selected text

        Returns:
            AgentResponse containing the answer and metadata
        """
        query_id = f"query_priority_{int(time.time() * 1000)}"
        agent_logger.log_query_processing(query_id, user_query.query_text, "RAG-Priority")

        start_time = time.time()

        # Explicitly check if selected text is provided and prioritize it (FR-005)
        if user_query.has_selected_text():
            logger.info(f"Selected text provided for query {query_id}, prioritizing over retrieval")
            agent_logger.log_retrieval_result(query_id, 1, "selected_text_priority")

            # Use selected text as primary context
            response = self.response_generator.generate_response_with_selected_text(
                user_query.selected_text,
                user_query.query_text
            )
        else:
            logger.info(f"No selected text for query {query_id}, using vector search")
            # Perform vector search to retrieve relevant context
            retrieved_context = self.search_service.search_by_text(
                user_query.query_text,
                limit=5
            )

            agent_logger.log_retrieval_result(query_id, len(retrieved_context.passages), "vector_search")

            # Generate response based on retrieved context
            response = self.response_generator.generate_response(
                retrieved_context,
                user_query.query_text
            )

        # Update processing time
        response.processing_time = time.time() - start_time

        # Validate the response
        is_valid = self.validator.validate_agent_response(response)
        agent_logger.log_validation_result(query_id, is_valid, "response_validation")

        if not is_valid:
            logger.warning(f"Response validation failed for priority query {query_id}, creating default response")
            response = AgentResponse(
                answer="I couldn't generate a proper response. Please try rephrasing your question.",
                source_references=[],
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                was_handoff=False
            )

        agent_logger.log_response_generation(
            query_id,
            len(response.answer),
            response.confidence_score
        )

        return response

    @log_execution_time
    def process_query_with_context(self, user_query: UserQuery, context: RetrievedContext) -> AgentResponse:
        """
        Process a user query with a pre-retrieved context

        Args:
            user_query: The user's query
            context: Pre-retrieved context to use for response generation

        Returns:
            AgentResponse containing the answer and metadata
        """
        query_id = f"query_ctx_{int(time.time() * 1000)}"

        start_time = time.time()

        # Generate response based on provided context
        response = self.response_generator.generate_response(context, user_query.query_text)

        # Update processing time
        response.processing_time = time.time() - start_time

        # Validate the response
        is_valid = self.validator.validate_agent_response(response)
        if not is_valid:
            logger.warning(f"Response validation failed for query with context {query_id}")

        return response

    def retrieve_context_only(self, query_text: str, limit: int = 5) -> RetrievedContext:
        """
        Only retrieve context without generating a response

        Args:
            query_text: The query text to search for
            limit: Maximum number of results to return

        Returns:
            RetrievedContext containing the relevant passages
        """
        query_id = f"retrieve_{int(time.time() * 1000)}"

        # Perform vector search to retrieve relevant context
        retrieved_context = self.search_service.search_by_text(query_text, limit)

        agent_logger.log_retrieval_result(query_id, len(retrieved_context.passages), "vector_search")
        return retrieved_context

    def process_query_with_summarization(self, user_query: UserQuery) -> AgentResponse:
        """
        Process a user query with summarization of multiple retrieved passages

        Args:
            user_query: The user's query with optional selected text

        Returns:
            AgentResponse containing the summarized answer and metadata
        """
        query_id = f"query_sum_{int(time.time() * 1000)}"

        start_time = time.time()

        if user_query.selected_text:
            # Use selected text as context
            response = self.response_generator.generate_response_with_selected_text(
                user_query.selected_text,
                user_query.query_text
            )
        else:
            # Retrieve context
            retrieved_context = self.search_service.search_by_text(
                user_query.query_text,
                limit=5
            )

            agent_logger.log_retrieval_result(query_id, len(retrieved_context.passages), "vector_search")

            # Generate summarized response
            response = self.response_generator.generate_summarized_response(
                retrieved_context,
                user_query.query_text
            )

        # Update processing time
        response.processing_time = time.time() - start_time

        # Validate the response
        is_valid = self.validator.validate_agent_response(response)
        if not is_valid:
            logger.warning(f"Summarized response validation failed for query {query_id}")

        return response

    def validate_pipeline_response(self, user_query: UserQuery, response: AgentResponse) -> bool:
        """
        Validate that a pipeline response meets all requirements

        Args:
            user_query: The original user query
            response: The response to validate

        Returns:
            True if the response is valid, False otherwise
        """
        # Validate basic response structure
        is_valid = self.validator.validate_agent_response(response)
        if not is_valid:
            return False

        # Validate grounding if context was used
        if not user_query.selected_text and hasattr(response, 'source_references') and response.source_references:
            context_text = " ".join([ref['passage'] for ref in response.source_references])
            is_grounded = self.validator.validate_grounding(response, context_text)
            return is_grounded

        return True


# Global instance for easy access
rag_pipeline = RAGPipeline()