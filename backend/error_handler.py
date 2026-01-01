"""
Error Handler for Backend Multi-Agent System for Book RAG Chatbot

This module provides standardized error response format and proper error handling
for all agent operations.
"""
from typing import Dict, Any, Optional
from enum import Enum
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """
    Enum for different types of errors
    """
    VALIDATION_ERROR = "validation_error"
    RETRIEVAL_ERROR = "retrieval_error"
    GENERATION_ERROR = "generation_error"
    COMMUNICATION_ERROR = "communication_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    INTERNAL_ERROR = "internal_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SECURITY_ERROR = "security_error"


class StandardizedError:
    """
    Class representing a standardized error response
    """

    def __init__(self, error_type: ErrorType, message: str, details: Optional[Dict[str, Any]] = None,
                 status_code: int = 500):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error to a dictionary for API response

        Returns:
            Dictionary representation of the error
        """
        return {
            "error": {
                "type": self.error_type.value,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp,
                "status_code": self.status_code
            }
        }

    def log_error(self, context: str = ""):
        """
        Log the error with appropriate severity

        Args:
            context: Context where the error occurred
        """
        log_message = f"Error [{self.error_type.value}] in {context}: {self.message}"
        if self.status_code >= 500:
            logger.error(log_message, extra={"error_details": self.details})
        elif self.status_code >= 400:
            logger.warning(log_message, extra={"error_details": self.details})
        else:
            logger.info(log_message, extra={"error_details": self.details})


class ErrorHandler:
    """
    Service for handling errors consistently across the application
    """

    def __init__(self):
        pass

    def handle_validation_error(self, message: str, field: Optional[str] = None) -> StandardizedError:
        """
        Handle validation errors

        Args:
            message: Error message
            field: Field that failed validation (optional)

        Returns:
            StandardizedError instance
        """
        details = {"field": field} if field else {}
        error = StandardizedError(
            error_type=ErrorType.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=400
        )
        error.log_error("validation")
        return error

    def handle_retrieval_error(self, message: str, query: Optional[str] = None) -> StandardizedError:
        """
        Handle retrieval errors

        Args:
            message: Error message
            query: Query that caused the error (optional)

        Returns:
            StandardizedError instance
        """
        details = {"query": query[:100] + "..." if query and len(query) > 100 else query} if query else {}
        error = StandardizedError(
            error_type=ErrorType.RETRIEVAL_ERROR,
            message=message,
            details=details,
            status_code=500
        )
        error.log_error("retrieval")
        return error

    def handle_generation_error(self, message: str, context: Optional[str] = None) -> StandardizedError:
        """
        Handle response generation errors

        Args:
            message: Error message
            context: Context that caused the error (optional)

        Returns:
            StandardizedError instance
        """
        details = {"context_length": len(context) if context else 0}
        error = StandardizedError(
            error_type=ErrorType.GENERATION_ERROR,
            message=message,
            details=details,
            status_code=500
        )
        error.log_error("generation")
        return error

    def handle_external_service_error(self, service_name: str, message: str) -> StandardizedError:
        """
        Handle external service errors (e.g., Qdrant, Cohere, Gemini)

        Args:
            service_name: Name of the external service
            message: Error message

        Returns:
            StandardizedError instance
        """
        details = {"service": service_name}
        error = StandardizedError(
            error_type=ErrorType.EXTERNAL_SERVICE_ERROR,
            message=message,
            details=details,
            status_code=503  # Service Unavailable
        )
        error.log_error(f"external_service_{service_name}")
        return error

    def handle_rate_limit_error(self, identifier: str, limit: int) -> StandardizedError:
        """
        Handle rate limit errors

        Args:
            identifier: Identifier that exceeded the limit
            limit: The rate limit that was exceeded

        Returns:
            StandardizedError instance
        """
        details = {"identifier": identifier, "limit": limit}
        error = StandardizedError(
            error_type=ErrorType.RATE_LIMIT_ERROR,
            message=f"Rate limit exceeded for {identifier}. Maximum {limit} requests per minute.",
            details=details,
            status_code=429
        )
        error.log_error("rate_limiting")
        return error

    def handle_internal_error(self, exception: Exception, context: str = "") -> StandardizedError:
        """
        Handle internal errors

        Args:
            exception: The exception that occurred
            context: Context where the error occurred

        Returns:
            StandardizedError instance
        """
        error_msg = str(exception)
        details = {
            "exception_type": type(exception).__name__,
            "context": context,
            "traceback": traceback.format_exc() if logger.level <= logging.DEBUG else "Traceback hidden"
        }

        error = StandardizedError(
            error_type=ErrorType.INTERNAL_ERROR,
            message=f"An internal error occurred: {error_msg}",
            details=details,
            status_code=500
        )
        error.log_error(context)
        return error

    def handle_security_error(self, message: str, threat_type: Optional[str] = None) -> StandardizedError:
        """
        Handle security-related errors

        Args:
            message: Error message
            threat_type: Type of security threat detected

        Returns:
            StandardizedError instance
        """
        details = {"threat_type": threat_type} if threat_type else {}
        error = StandardizedError(
            error_type=ErrorType.SECURITY_ERROR,
            message=message,
            details=details,
            status_code=400
        )
        error.log_error("security")
        return error

    def create_error_middleware(self, request, call_next):
        """
        Create error handling middleware for FastAPI

        Args:
            request: The incoming request
            call_next: The next function in the middleware chain

        Returns:
            Response or error
        """
        try:
            response = call_next(request)
            return response
        except Exception as e:
            # Handle the exception and return a standardized error response
            error = self.handle_internal_error(e, f"middleware_processing_{request.url.path}")
            return error.to_dict(), error.status_code


# Global instance for easy access
error_handler = ErrorHandler()