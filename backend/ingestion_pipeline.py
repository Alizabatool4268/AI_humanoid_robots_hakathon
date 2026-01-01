"""
Embedding Ingestion Pipeline for Backend Multi-Agent System for Book RAG Chatbot

This module provides functionality to store book content in Qdrant using embeddings.
"""
from typing import List, Dict, Any
from .qdrant_client import qdrant_client_wrapper
from .embedding_service import cohere_embedding_service
import logging
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

class EmbeddingIngestionPipeline:
    """
    Pipeline for ingesting book content and storing embeddings in Qdrant
    """

    def __init__(self):
        self.qdrant_client = qdrant_client_wrapper
        self.embedding_service = cohere_embedding_service

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks suitable for embedding

        Args:
            text: The text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks

        Returns:
            List of dictionaries with 'text' and 'metadata' keys
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk_text = text[start:end]

            # Add metadata about the chunk position
            chunk_data = {
                "text": chunk_text,
                "metadata": {
                    "start_pos": start,
                    "end_pos": end,
                    "chunk_id": str(uuid.uuid4())
                }
            }

            chunks.append(chunk_data)
            start = end - overlap

        logger.info(f"Text chunked into {len(chunks)} chunks")
        return chunks

    def process_book_content(self, book_content: str, book_metadata: Dict[str, Any]) -> List[str]:
        """
        Process book content by chunking, embedding, and storing in Qdrant

        Args:
            book_content: The full text content of the book
            book_metadata: Metadata about the book (title, author, etc.)

        Returns:
            List of IDs of the stored embeddings
        """
        # Chunk the book content
        chunks = self.chunk_text(book_content)

        # Add book-specific metadata to each chunk
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {**chunk["metadata"], **book_metadata}
            chunk_metadata["chunk_number"] = i
            processed_chunks.append({
                "text": chunk["text"],
                "metadata": chunk_metadata
            })

        # Generate embeddings for all chunks
        texts = [chunk["text"] for chunk in processed_chunks]
        embeddings = self.embedding_service.generate_embeddings(texts)

        # Store embeddings in Qdrant with their metadata
        stored_ids = []
        for chunk, embedding in zip(processed_chunks, embeddings):
            # In a real implementation, we'd use the actual embedding
            # For now, we'll update the storage method to accept the embedding
            text_id = self.qdrant_client.store_embedding_with_vector(
                embedding=embedding,
                text=chunk["text"],
                metadata=chunk["metadata"]
            )
            stored_ids.append(text_id)

        logger.info(f"Stored {len(stored_ids)} embeddings for book: {book_metadata.get('title', 'Unknown')}")
        return stored_ids

    def process_book_from_file(self, file_path: str, book_metadata: Dict[str, Any]) -> List[str]:
        """
        Process a book from a file by reading its content and ingesting it

        Args:
            file_path: Path to the book file
            book_metadata: Metadata about the book

        Returns:
            List of IDs of the stored embeddings
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Book file not found: {file_path}")

        # Read the book content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        logger.info(f"Read book content from {file_path}, length: {len(content)} characters")
        return self.process_book_content(content, book_metadata)

    def bulk_ingest_books(self, books_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Ingest multiple books at once

        Args:
            books_data: List of dictionaries with 'content' or 'file_path' and 'metadata' keys

        Returns:
            Dictionary mapping book titles to lists of stored embedding IDs
        """
        results = {}
        for book_data in books_data:
            try:
                title = book_data.get('metadata', {}).get('title', 'Unknown')

                if 'content' in book_data:
                    # Process from content string
                    stored_ids = self.process_book_content(
                        book_data['content'],
                        book_data['metadata']
                    )
                elif 'file_path' in book_data:
                    # Process from file
                    stored_ids = self.process_book_from_file(
                        book_data['file_path'],
                        book_data['metadata']
                    )
                else:
                    logger.warning(f"Book {title} has neither content nor file_path, skipping")
                    continue

                results[title] = stored_ids
                logger.info(f"Successfully ingested book: {title}")
            except Exception as e:
                logger.error(f"Failed to ingest book: {str(e)}")
                continue

        return results


# Extend the QdrantClientWrapper to support storing with actual vectors
def extend_qdrant_client():
    """
    Extend the QdrantClientWrapper with methods to store embeddings with actual vectors
    """
    original_store_embedding = qdrant_client_wrapper.store_embedding

    def store_embedding_with_vector(self, embedding: List[float], text: str, metadata: Dict[str, Any], text_id: str = None):
        if text_id is None:
            text_id = str(uuid.uuid4())

        from qdrant_client.http import models
        points = [
            models.PointStruct(
                id=text_id,
                vector=embedding,
                payload={
                    "text": text,
                    "metadata": metadata
                }
            )
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        logger.info(f"Stored embedding with vector for text ID: {text_id}")
        return text_id

    # Add the new method to the instance
    qdrant_client_wrapper.store_embedding_with_vector = store_embedding_with_vector.__get__(qdrant_client_wrapper, type(qdrant_client_wrapper))


# Initialize the extension
extend_qdrant_client()

# Global instance for easy access
embedding_ingestion_pipeline = EmbeddingIngestionPipeline()