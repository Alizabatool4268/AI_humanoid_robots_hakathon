"""
Backend Multi-Agent System for Book RAG Chatbot

This module implements a production-ready backend agent that routes book-related queries
via a triage agent to a query agent for RAG responses, ensuring deterministic, grounded answers.
All backend logic resides in this single file following OpenAI Agents SDK best practices.
"""
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

from models import UserQuery, AgentResponse, RetrievedContext, AgentState, AgentType
from gemini_service import gemini_service
from rag_agent import rag_pipeline
from utils import AgentLogger
from validators import api_response_validator

logger = logging.getLogger(__name__)
agent_logger = AgentLogger(__name__)

class TriageAgent:
    """
    Triage agent class for query classification
    """

    def __init__(self):
        self.gemini_service = gemini_service
        self.agent_type = AgentType.TRIAGE

    def classify_query(self, user_query: UserQuery) -> str:
        """
        Classify a user query to determine if it's book-related

        Args:
            user_query: The user's query to classify

        Returns:
            Classification result ("book-related" or "other")
        """
        query_id = f"triage_{int(datetime.now().timestamp() * 1000)}"

        agent_logger.log_query_processing(query_id, user_query.query_text, "Triage")

        try:
            classification = self.gemini_service.classify_query(user_query.query_text)

            agent_logger.logger.info(f"Triage agent classified query {query_id} as {classification}")

            return classification
        except Exception as e:
            logger.error(f"Error in triage classification: {str(e)}")
            # Default to book-related to ensure functionality
            return "book-related"

    def should_hand_off(self, classification: str) -> bool:
        """
        Determine if the query should be handed off to the query agent

        Args:
            classification: The classification result from classify_query

        Returns:
            True if the query should be handed off, False otherwise
        """
        return classification == "book-related"

    def determine_handoff_criteria(self, user_query: UserQuery) -> Dict[str, Any]:
        """
        Determine detailed handoff criteria for the query

        Args:
            user_query: The user's query to evaluate

        Returns:
            Dictionary with handoff criteria and reasoning
        """
        classification = self.gemini_service.classify_query(user_query.query_text)

        criteria = {
            "classification": classification,
            "should_handoff": classification == "book-related",
            "reasoning": f"Query classified as '{classification}', handoff {'required' if classification == 'book-related' else 'not required'}"
        }

        return criteria


class QueryAgent:
    """
    Query agent class for RAG processing
    """

    def __init__(self):
        self.rag_pipeline = rag_pipeline
        self.agent_type = AgentType.QUERY

    def process_query(self, user_query: UserQuery) -> AgentResponse:
        """
        Process a user query using the RAG pipeline

        Args:
            user_query: The user's query to process

        Returns:
            AgentResponse containing the answer and metadata
        """
        query_id = f"query_agent_{int(datetime.now().timestamp() * 1000)}"

        agent_logger.log_query_processing(query_id, user_query.query_text, "Query-Agent")

        try:
            # Process the query through the RAG pipeline
            response = self.rag_pipeline.process_query_with_priority_handling(user_query)

            # Mark that this response involved a handoff
            response.was_handoff = True

            agent_logger.log_response_generation(
                query_id,
                len(response.answer),
                response.confidence_score
            )

            return response
        except Exception as e:
            logger.error(f"Error in query agent processing: {str(e)}")

            # Return a safe response
            return AgentResponse(
                answer="An error occurred while processing your query. Please try again.",
                source_references=[],
                confidence_score=0.0,
                processing_time=0.0,
                was_handoff=True
            )


class AgentCommunicationProtocol:
    """
    Protocol for communication between agents in the multi-agent system
    """

    @staticmethod
    def format_query_for_agent(user_query: UserQuery, agent_type: AgentType) -> Dict[str, Any]:
        """
        Format a user query for a specific agent type

        Args:
            user_query: The original user query
            agent_type: The type of agent that will process the query

        Returns:
            Dictionary with query formatted for the specific agent
        """
        return {
            "query_text": user_query.query_text,
            "selected_text": user_query.selected_text,
            "user_context": user_query.user_context,
            "timestamp": user_query.timestamp.isoformat(),
            "target_agent": agent_type.value,
            "original_query_id": f"user_{int(user_query.timestamp.timestamp() * 1000)}"
        }

    @staticmethod
    def format_response_from_agent(response: AgentResponse, source_agent: AgentType) -> Dict[str, Any]:
        """
        Format a response from an agent for communication

        Args:
            response: The agent's response
            source_agent: The type of agent that generated the response

        Returns:
            Dictionary with response formatted for communication
        """
        return {
            "answer": response.answer,
            "source_references": response.source_references,
            "confidence_score": response.confidence_score,
            "processing_time": response.processing_time,
            "was_handoff": response.was_handoff,
            "source_agent": source_agent.value,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def validate_agent_communication(data: Dict[str, Any]) -> bool:
        """
        Validate that agent communication data is properly formatted

        Args:
            data: The communication data to validate

        Returns:
            True if valid, False otherwise
        """
        required_keys = ["timestamp", "source_agent"]
        for key in required_keys:
            if key not in data:
                return False
        return True


class MultiAgentSystem:
    """
    Main multi-agent system that coordinates between triage and query agents
    """

    def __init__(self):
        self.triage_agent = TriageAgent()
        self.query_agent = QueryAgent()
        self.validator = api_response_validator
        self.communication_protocol = AgentCommunicationProtocol()

    def process_user_query(self, user_query: UserQuery) -> AgentResponse:
        """
        Process a user query through the multi-agent system

        Args:
            user_query: The user's query to process

        Returns:
            AgentResponse containing the answer and metadata
        """
        query_id = f"multi_agent_{int(datetime.now().timestamp() * 1000)}"

        try:
            # Classify the query using the triage agent
            classification = self.triage_agent.classify_query(user_query)

            agent_logger.logger.info(f"Query {query_id} classified as: {classification}")

            # Determine if we should hand off to the query agent
            if self.triage_agent.should_hand_off(classification):
                agent_logger.log_agent_handoff(query_id, "Triage", "Query")

                # Process with the query agent
                response = self.query_agent.process_query(user_query)

                # Validate the response
                is_valid = self.validator.validate_agent_response(response)
                if not is_valid:
                    logger.warning(f"Response validation failed for multi-agent query {query_id}")

                return response
            else:
                # Return a response indicating the query was not book-related
                response = AgentResponse(
                    answer="This system is designed to answer questions about book content. Your query doesn't appear to be related to book content.",
                    source_references=[],
                    confidence_score=1.0,
                    processing_time=0.0,
                    was_handoff=False
                )

                agent_logger.logger.info(f"Query {query_id} was not book-related, returning informational response")
                return response

        except Exception as e:
            logger.error(f"Error in multi-agent processing for query {query_id}: {str(e)}")
            agent_logger.log_error(query_id, e, "Multi-agent processing")

            # Return a safe error response
            return AgentResponse(
                answer="An error occurred while processing your query through the multi-agent system. Please try again.",
                source_references=[],
                confidence_score=0.0,
                processing_time=0.0,
                was_handoff=False
            )

    def process_user_query_with_communication_error_handling(self, user_query: UserQuery) -> AgentResponse:
        """
        Process a user query through the multi-agent system with enhanced error handling

        Args:
            user_query: The user's query to process

        Returns:
            AgentResponse containing the answer and metadata
        """
        query_id = f"multi_agent_safe_{int(datetime.now().timestamp() * 1000)}"

        try:
            # Validate the communication protocol
            query_data = self.communication_protocol.format_query_for_agent(user_query, AgentType.TRIAGE)
            is_valid = self.communication_protocol.validate_agent_communication({"timestamp": query_data["timestamp"], "source_agent": "triage"})

            if not is_valid:
                logger.error(f"Invalid communication format for query {query_id}")
                raise ValueError("Invalid agent communication format")

            # Classify the query using the triage agent
            classification = self.triage_agent.classify_query(user_query)

            agent_logger.logger.info(f"Query {query_id} classified as: {classification}")

            # Determine if we should hand off to the query agent
            if self.triage_agent.should_hand_off(classification):
                agent_logger.log_agent_handoff(query_id, "Triage", "Query")

                # Format query for the query agent
                query_for_query_agent = self.communication_protocol.format_query_for_agent(user_query, AgentType.QUERY)

                # Process with the query agent
                response = self.query_agent.process_query(user_query)

                # Format response for communication
                response_data = self.communication_protocol.format_response_from_agent(response, AgentType.QUERY)

                # Validate the response
                is_valid = self.validator.validate_agent_response(response)
                if not is_valid:
                    logger.warning(f"Response validation failed for multi-agent query {query_id}")

                return response
            else:
                # Return a response indicating the query was not book-related
                response = AgentResponse(
                    answer="This system is designed to answer questions about book content. Your query doesn't appear to be related to book content.",
                    source_references=[],
                    confidence_score=1.0,
                    processing_time=0.0,
                    was_handoff=False
                )

                agent_logger.logger.info(f"Query {query_id} was not book-related, returning informational response")
                return response

        except Exception as e:
            logger.error(f"Error in multi-agent processing for query {query_id}: {str(e)}")
            agent_logger.log_error(query_id, e, "Multi-agent processing")

            # Return a safe error response
            return AgentResponse(
                answer="An error occurred while processing your query through the multi-agent system. Please try again.",
                source_references=[],
                confidence_score=0.0,
                processing_time=0.0,
                was_handoff=False
            )

    def process_query_with_state_tracking(self, user_query: UserQuery) -> AgentResponse:
        """
        Process a user query with explicit state tracking

        Args:
            user_query: The user's query to process

        Returns:
            AgentResponse containing the answer and metadata
        """
        # Create initial agent state
        agent_state = AgentState(
            current_agent=AgentType.TRIAGE,
            query_classification="unknown",
            processing_steps=["Started processing"]
        )

        query_id = f"stateful_{int(datetime.now().timestamp() * 1000)}"

        # Add step to state
        agent_state.processing_steps.append(f"Step 1: Triage agent classifying query")

        # Classify the query
        classification = self.triage_agent.classify_query(user_query)
        agent_state.query_classification = classification
        agent_state.processing_steps.append(f"Step 2: Query classified as {classification}")

        if self.triage_agent.should_hand_off(classification):
            agent_state.current_agent = AgentType.QUERY
            agent_state.processing_steps.append("Step 3: Handing off to query agent")

            # Process with query agent
            response = self.query_agent.process_query(user_query)
            response.was_handoff = True

            agent_state.processing_steps.append("Step 4: Query agent processing completed")
        else:
            # Non-book related query
            response = AgentResponse(
                answer="This system is designed to answer questions about book content. Your query doesn't appear to be related to book content.",
                source_references=[],
                confidence_score=1.0,
                processing_time=0.0,
                was_handoff=False
            )
            agent_state.processing_steps.append("Step 3: Query identified as non-book related")

        agent_logger.logger.info(f"Stateful processing completed for query {query_id}")
        return response


# Global instance for the multi-agent system
multi_agent_system = MultiAgentSystem()