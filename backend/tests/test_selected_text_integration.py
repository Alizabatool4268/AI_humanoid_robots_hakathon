"""
Integration tests for selected text override functionality in the Backend Multi-Agent System for Book RAG Chatbot
"""
import pytest
from backend.models import UserQuery, AgentResponse
from backend.rag_agent import rag_pipeline
from backend.agents import multi_agent_system
from backend.selected_text_service import selected_text_service


class TestSelectedTextIntegration:
    """
    Integration test class for verifying selected text always overrides retrieval
    """

    def test_selected_text_overrides_retrieval_in_rag_pipeline(self):
        """
        Test that selected text always overrides retrieval in the RAG pipeline
        """
        # Create a query that would normally retrieve different content
        query_text = "What is the meaning of life?"
        selected_text = "The meaning of life is specifically this: to find happiness in simple things."

        user_query = UserQuery(
            query_text=query_text,
            selected_text=selected_text
        )

        # Process through RAG pipeline with priority handling
        response = rag_pipeline.process_query_with_priority_handling(user_query)

        # The response should be based on the selected text, not retrieved content
        assert selected_text in response.source_references[0]["passage"] or \
               response.answer.lower().replace(" ", "") in selected_text.lower().replace(" ", "") or \
               selected_text.lower().replace(" ", "") in response.answer.lower().replace(" ", "")

        # Verify that the response was generated with high confidence
        assert response.confidence_score >= 0.7

    def test_selected_text_overrides_retrieval_in_multi_agent_system(self):
        """
        Test that selected text overrides retrieval in the multi-agent system
        """
        query_text = "What is the main character's motivation?"
        selected_text = "The main character's motivation is to protect his family at all costs."

        user_query = UserQuery(
            query_text=query_text,
            selected_text=selected_text
        )

        # Process through multi-agent system
        response = multi_agent_system.process_user_query(user_query)

        # The response should be based on the selected text
        assert selected_text in response.source_references[0]["passage"] or \
               response.answer.lower().replace(" ", "") in selected_text.lower().replace(" ", "") or \
               selected_text.lower().replace(" ", "") in response.answer.lower().replace(" ", "")

        # Verify that the response was generated with high confidence
        assert response.confidence_score >= 0.7

    def test_selected_text_processing_integration(self):
        """
        Test the full selected text processing pipeline
        """
        raw_selected_text = "This is the important text.  It has multiple   spaces and\ntabs."
        query = "What does this text say?"

        user_query = UserQuery(
            query_text=query,
            selected_text=raw_selected_text
        )

        # Preprocess the selected text
        processed_text = selected_text_service.preprocess_selected_text(raw_selected_text)

        # Validate the processed text
        is_valid = selected_text_service.validate_selected_text(processed_text)
        assert is_valid is True

        # Process through RAG pipeline
        response = rag_pipeline.process_query_with_priority_handling(user_query)

        # Verify that the response is grounded in the selected text
        assert len(response.source_references) > 0
        assert response.source_references[0]["source"] == "user_selected_text"

        # The response should make sense in context of the selected text
        assert response.answer != ""
        assert response.confidence_score >= 0.5

    def test_no_retrieval_when_selected_text_present(self):
        """
        Test that no retrieval happens when selected text is present
        """
        query_text = "What is the theme of the book?"  # Query that would normally trigger retrieval
        selected_text = "The theme is specifically about friendship and loyalty."

        user_query = UserQuery(
            query_text=query_text,
            selected_text=selected_text
        )

        # Process through the pipeline
        response = rag_pipeline.process_query_with_priority_handling(user_query)

        # Verify that the response source is from selected text, not retrieved content
        assert "user_selected_text" in [ref["source"] for ref in response.source_references]

        # The answer should be related to the selected text
        assert "friendship" in response.answer.lower() or "loyalty" in response.answer.lower()

    def test_selected_text_priority_over_retrieved_context(self):
        """
        Test that selected text has higher priority than retrieved context
        """
        # Create a scenario where both selected text and retrieved context exist
        query_text = "What is the main message?"
        selected_text = "The main message is clearly about courage."
        retrieved_context_text = "The book is about adventure and exploration."

        user_query = UserQuery(
            query_text=query_text,
            selected_text=selected_text
        )

        # Process the query
        response = rag_pipeline.process_query_with_priority_handling(user_query)

        # The response should prioritize the selected text over retrieved context
        response_contains_selected_theme = "courage" in response.answer.lower()
        response_contains_retrieved_theme = "adventure" in response.answer.lower() or "exploration" in response.answer.lower()

        # Selected text should take priority
        assert response_contains_selected_theme
        # Either retrieved theme is not in response, or selected theme takes precedence
        if response_contains_retrieved_theme:
            # If both themes are present, selected theme should be more prominent
            assert response.source_references[0]["source"] == "user_selected_text"