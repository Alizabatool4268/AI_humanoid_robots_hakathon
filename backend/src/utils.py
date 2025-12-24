"""Utility functions for the RAG pipeline"""

import re
import uuid
import time
from functools import wraps
import logging
from typing import List, Callable, Any


def count_words(text: str) -> int:
    """Count the number of words in a text string."""
    if not text:
        return 0
    # Split on whitespace and filter out empty strings
    words = [word for word in re.split(r'\s+', text.strip()) if word]
    return len(words)


def generate_chunk_id() -> str:
    """Generate a unique identifier for a text chunk."""
    return str(uuid.uuid4())


def split_by_sentences(text: str) -> List[str]:
    """Split text into sentences while preserving the sentence structure."""
    # Pattern to match sentence endings (., !, ?) followed by whitespace or end of string
    sentence_pattern = r'[.!?]+\s+|\.+\n|!+\n|\?+\n'
    sentences = re.split(sentence_pattern, text)

    # Reattach the sentence endings to each sentence
    sentence_ends = re.findall(sentence_pattern, text)

    result = []
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            if i < len(sentence_ends):
                result.append(sentence.strip() + sentence_ends[i].strip())
            else:
                result.append(sentence.strip())

    return [s for s in result if s.strip()]


def find_sentence_boundary(text: str, target_pos: int) -> int:
    """Find the nearest sentence boundary before or at the target position."""
    if target_pos >= len(text):
        return len(text)

    # Look backwards for sentence endings
    for i in range(target_pos, max(0, target_pos - 100), -1):  # Look back up to 100 chars
        if i < len(text) and text[i] in '.!?':
            # Check if this is followed by whitespace (end of sentence)
            if i + 1 < len(text) and (text[i + 1].isspace() or text[i + 1] == '\n'):
                return i + 1

    # If no sentence boundary found, return the original target
    return target_pos


def measure_performance(func: Callable) -> Callable:
    """
    Decorator to measure the execution time of a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper


def time_limited_execution(timeout_seconds: int = 10):
    """
    Decorator to ensure a function completes within a specified timeout.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time

            if execution_time > timeout_seconds:
                logging.warning(f"{func.__name__} took {execution_time:.4f} seconds, which exceeds the {timeout_seconds}s limit")
            else:
                logging.info(f"{func.__name__} completed within time limit ({execution_time:.4f}s/{timeout_seconds}s)")

            return result
        return wrapper
    return decorator