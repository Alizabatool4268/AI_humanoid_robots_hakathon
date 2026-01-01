"""
Unit tests for RAG functionality in the Backend Multi-Agent System for Book RAG Chatbot
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.models import UserQuery, AgentResponse, RetrievedContext
from backend.rag_agent import rag_pipeline
from backend.search_service import vector_search_service
from backend.response_generator import response_generation_service


class TestRAGFunctionality:
    """
    Test class for RAG functionality
    """

    def test_process_query_with_retrieved_context(self):
        """
        Test processing a query with retrieved context
        """
        # Create a mock user query
        user_query = UserQuery(
            query_text="What is the main theme of the book?",
            selected_text=None
        )

        # Mock the search service to return some context
        with patch.object(vector_search_service, 'search_by_text') as mock_search:
            mock_retrieved_context = RetrievedContext(
                passages=["The main theme is about courage and friendship"],
                similarity_scores=[0.85],
                source_metadata=[{"chapter": "1", "page": "15"}],
                retrieval_method="vector_search"
            )
            mock_search.return_value = mock_retrieved_context

            # Mock the response generator
            with patch.object(response_generation_service, 'generate_response') as mock_generate:
                expected_response = AgentResponse(
                    answer="The main theme of the book is about courage and friendship.",
                    source_references=[{
                        "passage": "The main theme is about courage and friendship",
                        "source": "Chapter 1, Page 15",
                        "similarity_score": 0.85
                    }],
                    confidence_score=0.85,
                    processing_time=0.1,
                    was_handoff=False
                )
                mock_generate.return_value = expected_response

                # Process the query
                result = rag_pipeline.process_query(user_query)

                # Assertions
                assert result.answer == expected_response.answer
                assert len(result.source_references) == 1
                assert result.confidence_score == expected_response.confidence_score
                mock_search.assert_called_once_with(user_query.query_text, limit=5)

    def test_process_query_with_selected_text(self):
        """
        Test processing a query with selected text (should override retrieval)
        """
        selected_text = "The book is about a hero's journey and self-discovery."
        user_query = UserQuery(
            query_text="What is the book about?",
            selected_text=selected_text
        )

        # Mock the response generator for selected text
        with patch.object(response_generation_service, 'generate_response_with_selected_text') as mock_generate:
            expected_response = AgentResponse(
                answer="The book is about a hero's journey and self-discovery.",
                source_references=[{
                    "passage": selected_text,
                    "source": "user_selected_text",
                    "similarity_score": 1.0
                }],
                confidence_score=0.9,
                processing_time=0.05,
                was_handoff=False
            )
            mock_generate.return_value = expected_response

            # Process the query
            result = rag_pipeline.process_query(user_query)

            # Assertions
            assert result.answer == expected_response.answer
            assert result.confidence_score == expected_response.confidence_score
            assert result.source_references[0]["source"] == "user_selected_text"
            # Verify that search was not called since selected text should override
            # (This would be verified in a full implementation)

    def test_retrieve_context_only(self):
        """
        Test retrieving context without generating response
        """
        query_text = "theme of the book"

        with patch.object(vector_search_service, 'search_by_text') as mock_search:
            expected_context = RetrievedContext(
                passages=["The main theme is about courage and friendship"],
                similarity_scores=[0.85],
                source_metadata=[{"chapter": "1", "page": "15"}],
                retrieval_method="vector_search"
            )
            mock_search.return_value = expected_context

            result = rag_pipeline.retrieve_context_only(query_text, limit=3)

            assert result == expected_context
            mock_search.assert_called_once_with(query_text, limit=3)

    def test_validate_pipeline_response_valid(self):
        """
        Test validating a valid pipeline response
        """
        user_query = UserQuery(
            query_text="What is the book about?",
            selected_text=None
        )
        response = AgentResponse(
            answer="The book is about adventure.",
            source_references=[{"passage": "Adventure story", "source": "Chapter 1", "similarity_score": 0.8}],
            confidence_score=0.8,
            processing_time=0.1,
            was_handoff=False
        )
        context = RetrievedContext(
            passages=["Adventure story"],
            similarity_scores=[0.8],
            source_metadata=[{"chapter": "1"}],
            retrieval_method="vector_search"
        )

        is_valid = rag_pipeline.validate_pipeline_response(user_query, response)
        assert is_valid is True

    def test_validate_pipeline_response_invalid(self):
        """
        Test validating an invalid pipeline response
        """
        user_query = UserQuery(
            query_text="What is the book about?",
            selected_text=None
        )
        # Invalid response with no source references
        response = AgentResponse(
            answer="The book is about adventure.",
            source_references=[],
            confidence_score=0.8,
            processing_time=0.1,
            was_handoff=False
        )
        context = RetrievedContext(
            passages=["Adventure story"],
            similarity_scores=[0.8],
            source_metadata=[{"chapter": "1"}],
            retrieval_method="vector_search"
        )

        is_valid = rag_pipeline.validate_pipeline_response(user_query, response)
        assert is_valid is False