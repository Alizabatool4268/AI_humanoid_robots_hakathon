"""Utility functions for the RAG pipeline"""

import re
import uuid
from typing import List


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