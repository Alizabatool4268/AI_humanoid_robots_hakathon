"""Text chunking module"""

import re
from typing import List, Dict, Any
from src.utils import count_words, generate_chunk_id
from src.logger import chunker_logger


def chunk_text(text: str, url: str, title: str, section: str) -> List[Dict]:
    """
    Split text content into semantically meaningful chunks of 300-500 words.

    Args:
        text: Raw text content to be chunked
        url: Source URL of the content
        title: Page title
        section: Section/heading hierarchy

    Returns:
        List of chunk dictionaries with content and metadata
    """
    if not text or count_words(text) == 0:
        chunker_logger.warning(f"No content to chunk for URL: {url}")
        return []

    chunks = []
    min_chunk_size = 300
    max_chunk_size = 500

    # Split text into sentences to respect sentence boundaries
    sentences = split_text_into_sentences(text)
    current_chunk = ""
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = count_words(sentence)

        # If adding this sentence would exceed max size
        if current_word_count + sentence_word_count > max_chunk_size and current_chunk:
            # Finalize the current chunk
            chunk = create_chunk(current_chunk.strip(), url, title, section)
            if chunk and validate_chunk_size(chunk):
                chunks.append(chunk)

            # Start a new chunk with the current sentence
            current_chunk = sentence
            current_word_count = sentence_word_count
        # If current chunk is empty or adding this sentence keeps us under max size
        elif current_word_count == 0 or current_word_count + sentence_word_count <= max_chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
            current_word_count += sentence_word_count
        # If we're under min size but adding more would exceed max
        else:
            # Finalize the current chunk even if it's under max size
            chunk = create_chunk(current_chunk.strip(), url, title, section)
            if chunk and validate_chunk_size(chunk):
                chunks.append(chunk)

            # Start a new chunk with the current sentence
            current_chunk = sentence
            current_word_count = sentence_word_count

    # Handle the last chunk if there's remaining content
    if current_chunk.strip():
        chunk = create_chunk(current_chunk.strip(), url, title, section)
        if chunk and validate_chunk_size(chunk):
            chunks.append(chunk)

    chunker_logger.info(f"Created {len(chunks)} valid chunks from content at {url}")
    return chunks


def split_text_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences while preserving sentence boundaries.

    Args:
        text: Text to split into sentences

    Returns:
        List of sentences
    """
    if not text:
        return []

    # Use regex to split on sentence boundaries (., !, ?) followed by whitespace
    # Keep the punctuation by using a capturing group
    sentence_pattern = r'([.!?]+)(?=\s|$|")'
    parts = re.split(sentence_pattern, text)

    sentences = []
    for i in range(0, len(parts), 2):
        if i < len(parts):
            sentence_text = parts[i]
            sentence_end = parts[i + 1] if i + 1 < len(parts) else ""

            # Combine the text and punctuation
            full_sentence = sentence_text + sentence_end

            # Only add non-empty sentences
            if full_sentence.strip():
                sentences.append(full_sentence.strip())

    # Filter out very short sentences that might be artifacts
    sentences = [s for s in sentences if len(s.strip()) > 10]

    return sentences


def create_chunk(content: str, url: str, title: str, section: str) -> Dict:
    """
    Create a chunk dictionary with all required metadata.

    Args:
        content: Chunk content
        url: Source URL
        title: Page title
        section: Section/heading

    Returns:
        Dictionary representing the chunk
    """
    chunk_id = generate_chunk_id()
    word_count = count_words(content)

    chunk = {
        "id": chunk_id,
        "content": content,
        "url": url,
        "title": title,
        "section": section,
        "word_count": word_count
    }

    chunker_logger.debug(f"Created chunk {chunk_id} with {word_count} words")
    return chunk


def validate_chunk_size(chunk: Dict, min_size: int = 300, max_size: int = 500) -> bool:
    """
    Validate that a chunk meets the size requirements.

    Args:
        chunk: Chunk dictionary to validate
        min_size: Minimum word count (default: 300)
        max_size: Maximum word count (default: 500)

    Returns:
        True if chunk size is valid, False otherwise
    """
    word_count = chunk.get('word_count', 0)
    return min_size <= word_count <= max_size