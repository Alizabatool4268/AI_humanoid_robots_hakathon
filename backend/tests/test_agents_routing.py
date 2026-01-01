"""
Unit tests for agent routing logic in the Backend Multi-Agent System for Book RAG Chatbot
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.models import UserQuery, AgentResponse, AgentState, AgentType
from backend.agents import TriageAgent, QueryAgent, MultiAgentSystem
from backend.gemini_service import gemini_service
from backend.rag_agent import rag_pipeline


class TestAgentRouting:
    """
    Test class for agent routing logic
    """

    def test_triage_agent_classify_book_related_query(self):
        """
        Test that the triage agent correctly classifies book-related queries
        """
        triage_agent = TriageAgent()

        # Mock the gemini service to return "book-related"
        with patch.object(gemini_service, 'classify_query') as mock_classify:
            mock_classify.return_value = "book-related"

            user_query = UserQuery(
                query_text="What is the theme of this novel?",
                selected_text=None
            )

            result = triage_agent.classify_query(user_query)

            assert result == "book-related"
            mock_classify.assert_called_once_with(user_query.query_text)

    def test_triage_agent_classify_non_book_query(self):
        """
        Test that the triage agent correctly classifies non-book-related queries
        """
        triage_agent = TriageAgent()

        # Mock the gemini service to return "other"
        with patch.object(gemini_service, 'classify_query') as mock_classify:
            mock_classify.return_value = "other"

            user_query = UserQuery(
                query_text="What's the weather today?",
                selected_text=None
            )

            result = triage_agent.classify_query(user_query)

            assert result == "other"
            mock_classify.assert_called_once_with(user_query.query_text)

    def test_triage_agent_should_handoff_book_related(self):
        """
        Test that triage agent determines to hand off book-related queries
        """
        triage_agent = TriageAgent()

        result = triage_agent.should_hand_off("book-related")

        assert result is True

    def test_triage_agent_should_not_handoff_other(self):
        """
        Test that triage agent does not hand off non-book-related queries
        """
        triage_agent = TriageAgent()

        result = triage_agent.should_hand_off("other")

        assert result is False

    def test_query_agent_process_query(self):
        """
        Test that the query agent processes queries using the RAG pipeline
        """
        query_agent = QueryAgent()

        user_query = UserQuery(
            query_text="What is the main character's name?",
            selected_text=None
        )

        expected_response = AgentResponse(
            answer="The main character's name is John.",
            source_references=[{"passage": "John is the main character", "source": "Chapter 1", "similarity_score": 0.9}],
            confidence_score=0.85,
            processing_time=0.2,
            was_handoff=True
        )

        # Mock the RAG pipeline
        with patch.object(query_agent.rag_pipeline, 'process_query_with_priority_handling') as mock_process:
            mock_process.return_value = expected_response

            result = query_agent.process_query(user_query)

            assert result == expected_response
            assert result.was_handoff is True  # Should be marked as handoff
            mock_process.assert_called_once_with(user_query)

    def test_multi_agent_system_process_book_related_query(self):
        """
        Test that the multi-agent system routes book-related queries to query agent
        """
        multi_agent_system = MultiAgentSystem()

        user_query = UserQuery(
            query_text="What is the central theme?",
            selected_text=None
        )

        # Mock triage agent to classify as book-related
        with patch.object(multi_agent_system.triage_agent, 'classify_query') as mock_classify:
            mock_classify.return_value = "book-related"

            with patch.object(multi_agent_system.triage_agent, 'should_hand_off') as mock_should_handoff:
                mock_should_handoff.return_value = True

                expected_response = AgentResponse(
                    answer="The central theme is about growth.",
                    source_references=[{"passage": "theme of growth", "source": "Chapter 2", "similarity_score": 0.8}],
                    confidence_score=0.8,
                    processing_time=0.3,
                    was_handoff=True
                )

                # Mock query agent to return the expected response
                with patch.object(multi_agent_system.query_agent, 'process_query') as mock_query_process:
                    mock_query_process.return_value = expected_response

                    result = multi_agent_system.process_user_query(user_query)

                    assert result == expected_response
                    mock_query_process.assert_called_once_with(user_query)

    def test_multi_agent_system_process_non_book_query(self):
        """
        Test that the multi-agent system handles non-book-related queries appropriately
        """
        multi_agent_system = MultiAgentSystem()

        user_query = UserQuery(
            query_text="What's the weather?",
            selected_text=None
        )

        # Mock triage agent to classify as "other"
        with patch.object(multi_agent_system.triage_agent, 'classify_query') as mock_classify:
            mock_classify.return_value = "other"

            with patch.object(multi_agent_system.triage_agent, 'should_hand_off') as mock_should_handoff:
                mock_should_handoff.return_value = False

                result = multi_agent_system.process_user_query(user_query)

                # Should return a non-book related response
                assert "book content" in result.answer.lower()
                assert result.was_handoff is False

    def test_determine_handoff_criteria(self):
        """
        Test that triage agent can determine detailed handoff criteria
        """
        triage_agent = TriageAgent()

        user_query = UserQuery(
            query_text="What happens in chapter 3?",
            selected_text=None
        )

        # Mock classification
        with patch.object(gemini_service, 'classify_query') as mock_classify:
            mock_classify.return_value = "book-related"

            result = triage_agent.determine_handoff_criteria(user_query)

            assert result["classification"] == "book-related"
            assert result["should_handoff"] is True
            assert "required" in result["reasoning"]

    def test_process_query_with_state_tracking(self):
        """
        Test processing with explicit state tracking
        """
        multi_agent_system = MultiAgentSystem()

        user_query = UserQuery(
            query_text="Tell me about the protagonist.",
            selected_text=None
        )

        # Mock triage agent to classify as book-related
        with patch.object(multi_agent_system.triage_agent, 'classify_query') as mock_classify:
            mock_classify.return_value = "book-related"

            with patch.object(multi_agent_system.triage_agent, 'should_hand_off') as mock_should_handoff:
                mock_should_handoff.return_value = True

                expected_response = AgentResponse(
                    answer="The protagonist is a brave hero.",
                    source_references=[{"passage": "brave hero", "source": "Character description", "similarity_score": 0.9}],
                    confidence_score=0.85,
                    processing_time=0.25,
                    was_handoff=True
                )

                # Mock query agent
                with patch.object(multi_agent_system.query_agent, 'process_query') as mock_query_process:
                    mock_query_process.return_value = expected_response

                    result = multi_agent_system.process_query_with_state_tracking(user_query)

                    assert result == expected_response

    def test_error_handling_in_multi_agent_processing(self):
        """
        Test error handling in multi-agent processing
        """
        multi_agent_system = MultiAgentSystem()

        user_query = UserQuery(
            query_text="What is the book about?",
            selected_text=None
        )

        # Force an exception in the process
        with patch.object(multi_agent_system.triage_agent, 'classify_query') as mock_classify:
            mock_classify.side_effect = Exception("Test error")

            result = multi_agent_system.process_user_query(user_query)

            # Should return a safe error response
            assert "error occurred" in result.answer.lower()
            assert result.confidence_score == 0.0
            assert result.was_handoff is False