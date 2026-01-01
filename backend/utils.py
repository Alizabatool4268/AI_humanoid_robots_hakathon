"""
Utilities for Backend Multi-Agent System for Book RAG Chatbot

This module provides logging and monitoring utilities for agent operations.
"""
import logging
import time
from typing import Callable, Any, Dict
from functools import wraps
import json
from datetime import datetime


def setup_logging():
    """
    Set up the logging configuration for the agent system
    """
    # Create a custom format for logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Output to console
            # In production, you might also add a file handler
        ]
    )


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log the execution time of functions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        logger = logging.getLogger(func.__module__)
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")

        return result
    return wrapper


def log_agent_operation(operation_name: str):
    """
    Decorator to log agent operations with additional context
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            logger.info(f"Starting agent operation: {operation_name}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time

                logger.info(f"Completed agent operation: {operation_name} in {execution_time:.4f}s")
                return result
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.error(f"Failed agent operation: {operation_name} after {execution_time:.4f}s - {str(e)}")
                raise
        return wrapper
    return decorator


class PerformanceMonitor:
    """
    A utility class for monitoring performance metrics
    """

    def __init__(self):
        self.metrics = {}

    def start_timer(self, operation: str) -> str:
        """
        Start a timer for an operation and return a timer ID

        Args:
            operation: Name of the operation being timed

        Returns:
            Timer ID that can be used to stop the timer
        """
        timer_id = f"{operation}_{int(time.time() * 1000000)}"
        self.metrics[timer_id] = {
            'operation': operation,
            'start_time': time.time(),
            'completed': False
        }
        return timer_id

    def stop_timer(self, timer_id: str) -> float:
        """
        Stop a timer and return the elapsed time

        Args:
            timer_id: ID returned by start_timer

        Returns:
            Elapsed time in seconds
        """
        if timer_id not in self.metrics:
            raise ValueError(f"Timer ID {timer_id} not found")

        if self.metrics[timer_id]['completed']:
            return self.metrics[timer_id]['elapsed_time']

        end_time = time.time()
        start_time = self.metrics[timer_id]['start_time']
        elapsed_time = end_time - start_time

        self.metrics[timer_id].update({
            'end_time': end_time,
            'elapsed_time': elapsed_time,
            'completed': True
        })

        # Log the performance metric
        operation = self.metrics[timer_id]['operation']
        logger = logging.getLogger(__name__)
        logger.info(f"Performance metric - {operation}: {elapsed_time:.4f}s")

        return elapsed_time

    def get_average_time(self, operation: str) -> float:
        """
        Get the average execution time for an operation

        Args:
            operation: Name of the operation

        Returns:
            Average execution time in seconds, or 0 if no metrics available
        """
        operation_metrics = [
            m for m in self.metrics.values()
            if m['operation'] == operation and m['completed']
        ]

        if not operation_metrics:
            return 0.0

        total_time = sum(m['elapsed_time'] for m in operation_metrics)
        return total_time / len(operation_metrics)

    def is_performance_acceptable(self, operation: str, threshold: float = 5.0) -> bool:
        """
        Check if the average performance for an operation is acceptable

        Args:
            operation: Name of the operation to check
            threshold: Maximum acceptable average time in seconds

        Returns:
            True if performance is acceptable, False otherwise
        """
        avg_time = self.get_average_time(operation)
        return avg_time <= threshold

    def get_performance_report(self) -> Dict[str, Dict[str, float]]:
        """
        Get a comprehensive performance report

        Returns:
            Dictionary with performance metrics for all operations
        """
        report = {}
        for operation in set(m['operation'] for m in self.metrics.values() if m['completed']):
            operation_metrics = [
                m for m in self.metrics.values()
                if m['operation'] == operation and m['completed']
            ]

            if operation_metrics:
                times = [m['elapsed_time'] for m in operation_metrics]
                report[operation] = {
                    'count': len(times),
                    'average': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'total': sum(times)
                }

        return report


class AgentLogger:
    """
    A specialized logger for agent operations with structured logging
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.performance_monitor = PerformanceMonitor()

    def log_query_processing(self, query_id: str, query_text: str, agent_type: str):
        """
        Log a query processing event
        """
        self.logger.info(f"Processing query {query_id} with {agent_type} agent: '{query_text[:50]}...'")

    def log_retrieval_result(self, query_id: str, num_passages: int, retrieval_method: str):
        """
        Log a retrieval result
        """
        self.logger.info(f"Retrieved {num_passages} passages for query {query_id} using {retrieval_method}")

    def log_response_generation(self, query_id: str, response_length: int, confidence: float):
        """
        Log a response generation event
        """
        self.logger.info(f"Generated response for query {query_id} with confidence {confidence:.2f}, length {response_length}")

    def log_agent_handoff(self, query_id: str, from_agent: str, to_agent: str):
        """
        Log an agent handoff event
        """
        self.logger.info(f"Handing off query {query_id} from {from_agent} agent to {to_agent} agent")

    def log_error(self, query_id: str, error: Exception, context: str = ""):
        """
        Log an error with context
        """
        self.logger.error(f"Error processing query {query_id} in {context}: {str(error)}")

    def log_validation_result(self, query_id: str, is_valid: bool, validation_type: str):
        """
        Log a validation result
        """
        status = "PASSED" if is_valid else "FAILED"
        self.logger.info(f"Validation {validation_type} for query {query_id}: {status}")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Setup logging when this module is imported
setup_logging()