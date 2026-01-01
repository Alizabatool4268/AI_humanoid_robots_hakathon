"""
Rate Limiter for Backend Multi-Agent System for Book RAG Chatbot

This module provides rate limiting middleware to prevent abuse of the API endpoints.
"""
import time
from typing import Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple rate limiter to prevent API abuse
    """

    def __init__(self, requests_per_minute: int = 100, window_size: int = 60):
        """
        Initialize the rate limiter

        Args:
            requests_per_minute: Maximum number of requests allowed per minute
            window_size: Time window in seconds
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.requests = defaultdict(list)  # ip_address -> [request_timestamps]

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if a request from the given identifier is allowed

        Args:
            identifier: Identifier for the requester (e.g., IP address)

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()

        # Clean up old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_size
        ]

        # Check if the number of requests is within the limit
        if len(self.requests[identifier]) < self.requests_per_minute:
            # Add current request
            self.requests[identifier].append(current_time)
            return True
        else:
            logger.warning(f"Rate limit exceeded for identifier: {identifier}")
            return False

    def get_remaining_requests(self, identifier: str) -> int:
        """
        Get the number of remaining requests for the identifier in the current window

        Args:
            identifier: Identifier for the requester

        Returns:
            Number of remaining requests allowed
        """
        current_time = time.time()

        # Clean up old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.window_size
        ]

        return max(0, self.requests_per_minute - len(self.requests[identifier]))

    def get_reset_time(self, identifier: str) -> float:
        """
        Get the time when the rate limit will reset for the identifier

        Args:
            identifier: Identifier for the requester

        Returns:
            Unix timestamp when the rate limit will reset
        """
        if identifier not in self.requests:
            return time.time()

        # Find the earliest request in the current window
        current_time = time.time()
        if not self.requests[identifier]:
            return current_time

        # Reset time is the earliest request time + window_size
        earliest_request = min(self.requests[identifier])
        reset_time = earliest_request + self.window_size

        return reset_time


# Global instance for rate limiting
rate_limiter = RateLimiter()