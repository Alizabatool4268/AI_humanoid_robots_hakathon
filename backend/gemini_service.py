"""
Gemini Service Wrapper for Backend Multi-Agent System for Book RAG Chatbot

This module provides a wrapper around the Google Generative AI (Gemini) service
for classification and text generation tasks.
"""
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service class for using Google's Gemini model for classification and generation
    """

    def __init__(self):
        """
        Initialize the Gemini client
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=api_key)
        self.model_name = "gemini-pro"  # Using Gemini Pro for text generation
        self.model = genai.GenerativeModel(self.model_name)

    def classify_query(self, query: str) -> str:
        """
        Classify a user query to determine if it's book-related

        Args:
            query: The user's query

        Returns:
            Classification result ("book-related" or "other")
        """
        try:
            prompt = f"""
            Classify the following query as either "book-related" or "other":

            Query: "{query}"

            A query is "book-related" if it asks about content in a book, seeks information
            from a book, or is about book-related topics. Otherwise, classify as "other".

            Classification:
            """

            response = self.model.generate_content(prompt)
            classification = response.text.strip().lower()

            # Normalize the response to expected values
            if "book" in classification or "book-related" in classification:
                result = "book-related"
            elif "other" in classification:
                result = "other"
            else:
                # Default to book-related for queries that seem relevant
                result = "book-related"
                logger.info(f"Uncertain classification '{classification}' defaulted to 'book-related' for query: {query}")

            logger.info(f"Classified query '{query[:50]}...' as {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to classify query: {str(e)}")
            # Default to book-related in case of error to ensure functionality
            return "book-related"

    def generate_response(self, context: str, query: str) -> str:
        """
        Generate a response based on the provided context and query

        Args:
            context: The context to use for generating the response
            query: The user's query

        Returns:
            Generated response text
        """
        try:
            prompt = f"""
            Based on the following context, answer the user's query.
            Only use information from the provided context.
            If the context doesn't contain information to answer the query,
            respond with "No relevant content found".

            Context: {context}

            Query: {query}

            Answer:
            """

            response = self.model.generate_content(prompt)
            generated_text = response.text.strip()

            logger.info(f"Generated response for query: {query[:50]}...")
            return generated_text
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise

    def validate_grounding(self, response: str, context: str) -> bool:
        """
        Validate that the response is grounded in the provided context

        Args:
            response: The generated response
            context: The context used to generate the response

        Returns:
            True if the response appears to be grounded in the context, False otherwise
        """
        try:
            # Simple validation: check if response contains key terms from context
            # In a real implementation, this would use more sophisticated grounding validation
            context_lower = context.lower()
            response_lower = response.lower()

            # Count overlapping words
            context_words = set(context_lower.split())
            response_words = set(response_lower.split())
            common_words = context_words.intersection(response_words)

            # If more than 30% of response words appear in context, consider it grounded
            if len(response_words) == 0:
                return False

            overlap_ratio = len(common_words) / len(response_words)
            is_valid = overlap_ratio > 0.3

            logger.info(f"Response grounding validation: {overlap_ratio:.2%} overlap, valid: {is_valid}")
            return is_valid
        except Exception as e:
            logger.error(f"Failed to validate grounding: {str(e)}")
            return True  # Default to True to not block responses in case of validation error


# Global instance for easy access
gemini_service = GeminiService()