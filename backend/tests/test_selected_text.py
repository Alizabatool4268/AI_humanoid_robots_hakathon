"""
Unit tests for selected text override functionality in the Backend Multi-Agent System for Book RAG Chatbot
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.models import UserQuery, AgentResponse, RetrievedContext
from backend.selected_text_service import selected_text_service
from backend.rag_agent import rag_pipeline
from backend.response_generator import response_generation_service


class TestSelectedTextFunctionality:
    """
    Test class for selected text override functionality
    """

    def test_process_selected_text(self):
        """
        Test processing selected text to create RetrievedContext
        """
        selected_text = "This is the selected text that should be used as context."
        query = "What does this text mean?"

        result = selected_text_service.process_selected_text(selected_text, query)

        assert len(result.passages) == 1
        assert result.passages[0] == selected_text
        assert result.similarity_scores[0] == 1.0
        assert result.retrieval_method == "selected_text"
        assert result.source_metadata[0]["source"] == "user_selected_text"

    def test_validate_selected_text_valid(self):
        """
        Test validating valid selected text
        """
        valid_text = "This is a valid selected text that is longer than 10 characters."

        is_valid = selected_text_service.validate_selected_text(valid_text)
        assert is_valid is True

    def test_validate_selected_text_invalid_short(self):
        """
        Test validating invalid selected text that is too short
        """
        short_text = "Too short"

        is_valid = selected_text_service.validate_selected_text(short_text)
        assert is_valid is False

    def test_validate_selected_text_invalid_empty(self):
        """
        Test validating empty selected text
        """
        empty_text = ""

        is_valid = selected_text_service.validate_selected_text(empty_text)
        assert is_valid is False

    def test_preprocess_selected_text(self):
        """
        Test preprocessing selected text
        """
        raw_text = "\tThis is   raw text\n\nwith\tmultiple   spaces.\n\n\nAnd newlines."
        expected = "  This is   raw text\n\nwith  multiple   spaces.\n\nAnd newlines."

        result = selected_text_service.preprocess_selected_text(raw_text)

        assert result == expected

    def test_create_context_from_multiple_selections(self):
        """
        Test creating context from multiple selected texts
        """
        selected_texts = [
            "First selected text.",
            "Second selected text that is longer than 10 characters."
        ]

        result = selected_text_service.create_context_from_multiple_selections(selected_texts)

        assert len(result.passages) == 2
        assert result.passages[0] == selected_texts[0]
        assert result.passages[1] == selected_texts[1]
        assert all(score == 1.0 for score in result.similarity_scores)
        assert result.retrieval_method == "selected_text"

    def test_process_query_with_selected_text_override(self):
        """
        Test that queries with selected text override general retrieval
        """
        selected_text = "The answer is specifically in this selected text."
        user_query = UserQuery(
            query_text="What is the answer?",
            selected_text=selected_text
        )

        # Mock the response generator to ensure selected text is used
        with patch.object(response_generation_service, 'generate_response_with_selected_text') as mock_gen_selected:
            expected_response = AgentResponse(
                answer="The answer is specifically in this selected text.",
                source_references=[{
                    "passage": selected_text,
                    "source": "user_selected_text",
                    "similarity_score": 1.0
                }],
                confidence_score=0.9,
                processing_time=0.05,
                was_handoff=False
            )
            mock_gen_selected.return_value = expected_response

            result = rag_pipeline.process_query(user_query)

            # Verify that the selected text response generator was called
            mock_gen_selected.assert_called_once_with(selected_text, user_query.query_text)
            assert result == expected_response

    def test_selected_text_has_priority_handling(self):
        """
        Test that selected text has priority handling in the pipeline
        """
        selected_text = "Priority text that should override retrieval."
        user_query = UserQuery(
            query_text="What does this say?",
            selected_text=selected_text
        )

        result = rag_pipeline.process_query_with_priority_handling(user_query)

        # The result should be based on selected text, not retrieved context
        assert result.was_handoff is False  # Since it's direct from selected text