"""Logging configuration for the RAG pipeline"""

import logging
import sys
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.

    Args:
        name: Name of the logger
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if logger already exists
    if logger.handlers:
        return logger

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


# Predefined loggers for different modules
pipeline_logger = setup_logger("pipeline")
crawler_logger = setup_logger("crawler")
extractor_logger = setup_logger("extractor")
chunker_logger = setup_logger("chunker")
embedder_logger = setup_logger("embedder")
storage_logger = setup_logger("storage")