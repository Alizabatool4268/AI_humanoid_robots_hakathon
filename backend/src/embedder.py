"""Cohere embedding generation module"""

import cohere
from typing import List, Dict, Any
from src.config.settings import Settings
from src.logger import embedder_logger
import time


def embed(chunks: List[Dict]) -> List[Dict]:
    """
    Generate Cohere embeddings for text chunks.

    Args:
        chunks: List of text chunks with metadata

    Returns:
        List of chunks with added embedding vectors
    """
    settings = Settings()
    settings.validate()

    # Initialize Cohere client
    co = cohere.Client(settings.COHERE_API_KEY)

    embedder_logger.info(f"Starting embedding generation for {len(chunks)} chunks")

    # Process chunks in batches to respect API limits
    batch_size = settings.BATCH_SIZE
    results = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_texts = [chunk['content'] for chunk in batch]

        try:
            # Generate embeddings for the batch
            response = co.embed(
                texts=batch_texts,
                model=settings.COHERE_MODEL,
                input_type="search_document"  # Appropriate for document search
            )

            # Add embeddings to chunks
            for idx, chunk in enumerate(batch):
                chunk_with_embedding = chunk.copy()
                chunk_with_embedding['vector'] = response.embeddings[idx]
                chunk_with_embedding['embedding_model'] = settings.COHERE_MODEL
                results.append(chunk_with_embedding)

            embedder_logger.info(f"Completed embedding for batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")

            # Respect rate limits
            if i + batch_size < len(chunks):
                time.sleep(settings.REQUEST_DELAY)

        except Exception as e:
            embedder_logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")
            raise

    embedder_logger.info(f"Successfully generated embeddings for {len(results)} chunks")
    return results