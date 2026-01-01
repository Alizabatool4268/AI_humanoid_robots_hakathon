"""
Input Sanitizer for Backend Multi-Agent System for Book RAG Chatbot

This module provides comprehensive input sanitization to prevent injection attacks
and ensure clean input for the agent system.
"""
import re
from typing import Union, List, Dict, Any
import html
import logging

logger = logging.getLogger(__name__)

class InputSanitizer:
    """
    Service for sanitizing user inputs to prevent injection attacks
    """

    def __init__(self):
        # Define patterns for potentially dangerous content
        self.dangerous_patterns = [
            r'<script.*?>.*?</script>',  # JavaScript
            r'javascript:',              # JavaScript protocol
            r'on\w+\s*=',               # Event handlers
            r'eval\s*\(',               # eval function
            r'expression\s*\(',         # CSS expression
            r'vbscript:',               # VBScript
            r'alert\s*\(',              # alert function
            r'document\.cookie',         # Document cookie access
            r'window\.',                # Window object access
            r'location\.',               # Location object access
        ]

        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.dangerous_patterns]

    def sanitize_text(self, text: str) -> str:
        """
        Sanitize a text input by removing or escaping dangerous content

        Args:
            text: The text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return text

        # HTML escape the text
        sanitized = html.escape(text, quote=True)

        # Remove dangerous patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(sanitized)
            if matches:
                logger.warning(f"Dangerous patterns detected and removed: {matches}")
                sanitized = pattern.sub('', sanitized)

        # Remove control characters except common whitespace
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)

        logger.info(f"Sanitized text of length {len(text)} -> {len(sanitized)}")
        return sanitized

    def sanitize_query(self, query: str) -> str:
        """
        Sanitize a user query specifically

        Args:
            query: The query to sanitize

        Returns:
            Sanitized query
        """
        if not query:
            return query

        # Apply general text sanitization
        sanitized = self.sanitize_text(query)

        # Additional query-specific sanitization
        # Remove potential SQL injection patterns
        sql_injection_patterns = [
            r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b',
            r'--',  # SQL comment
            r';',   # Statement terminator
        ]

        for pattern in sql_injection_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

        logger.info("Query sanitized successfully")
        return sanitized

    def sanitize_selected_text(self, selected_text: str) -> str:
        """
        Sanitize selected text input

        Args:
            selected_text: The selected text to sanitize

        Returns:
            Sanitized selected text
        """
        if not selected_text:
            return selected_text

        # Apply general text sanitization
        sanitized = self.sanitize_text(selected_text)

        logger.info("Selected text sanitized successfully")
        return sanitized

    def validate_and_sanitize_user_input(self, user_input: Union[str, Dict[str, Any], List[Any]]) -> Union[str, Dict[str, Any], List[Any]]:
        """
        Validate and sanitize various types of user input

        Args:
            user_input: The user input to sanitize (string, dict, or list)

        Returns:
            Sanitized user input
        """
        if isinstance(user_input, str):
            return self.sanitize_text(user_input)
        elif isinstance(user_input, dict):
            sanitized_dict = {}
            for key, value in user_input.items():
                # Sanitize both keys and values
                sanitized_key = self.sanitize_text(str(key)) if isinstance(key, str) else key
                sanitized_value = self.validate_and_sanitize_user_input(value)
                sanitized_dict[sanitized_key] = sanitized_value
            return sanitized_dict
        elif isinstance(user_input, list):
            return [self.validate_and_sanitize_user_input(item) for item in user_input]
        else:
            # For non-string types, return as is
            return user_input

    def check_for_malicious_content(self, text: str) -> Dict[str, Any]:
        """
        Check text for potentially malicious content without sanitizing

        Args:
            text: The text to check

        Returns:
            Dictionary with check results
        """
        results = {
            "is_safe": True,
            "dangerous_patterns_found": [],
            "risk_level": "low"  # low, medium, high
        }

        if not text:
            return results

        total_matches = 0
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(text)
            if matches:
                results["dangerous_patterns_found"].append({
                    "pattern": self.dangerous_patterns[i],
                    "matches": matches
                })
                total_matches += len(matches)

        if total_matches > 0:
            results["is_safe"] = False
            if total_matches <= 2:
                results["risk_level"] = "medium"
            else:
                results["risk_level"] = "high"

        return results

    def sanitize_user_context(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize user context data

        Args:
            user_context: The user context to sanitize

        Returns:
            Sanitized user context
        """
        if not user_context:
            return user_context

        sanitized_context = {}
        for key, value in user_context.items():
            # Sanitize the key
            sanitized_key = self.sanitize_text(str(key)) if isinstance(key, str) else key

            # Sanitize the value based on its type
            if isinstance(value, str):
                sanitized_value = self.sanitize_text(value)
            elif isinstance(value, (dict, list)):
                sanitized_value = self.validate_and_sanitize_user_input(value)
            else:
                sanitized_value = value

            sanitized_context[sanitized_key] = sanitized_value

        logger.info("User context sanitized successfully")
        return sanitized_context


# Global instance for easy access
input_sanitizer = InputSanitizer()