"""
Vector Search Service for Backend Multi-Agent System for Book RAG Chatbot

This module provides vector search functionality to retrieve relevant passages from book content.
"""
from typing import List, Dict, Any, Optional
from qdrant_wrapper import qdrant_client_wrapper
from embedding_service import cohere_embedding_service
from models import RetrievedContext
import logging

logger = logging.getLogger(__name__)

class VectorSearchService:
    """
    Service for performing vector similarity search in Qdrant
    """

    def __init__(self):
        self.qdrant_client = qdrant_client_wrapper
        self.embedding_service = cohere_embedding_service

    def search_by_text(self, query_text: str, limit: int = 5) -> RetrievedContext:
        """
        Search for relevant passages using text query

        Args:
            query_text: The text to search for similar passages
            limit: Maximum number of results to return

        Returns:
            RetrievedContext containing the relevant passages and metadata
        """
        # Generate embedding for the query text
        query_embedding = self.embedding_service.generate_embedding(query_text)

        # Perform vector search in Qdrant
        search_results = self.qdrant_client.search_similar(query_embedding, limit=limit)

        # Extract passages, similarity scores, and metadata
        passages = [result["text"] for result in search_results]
        similarity_scores = [result["similarity_score"] for result in search_results]
        source_metadata = [result["metadata"] for result in search_results]

        # Create and return RetrievedContext
        retrieved_context = RetrievedContext(
            passages=passages,
            similarity_scores=similarity_scores,
            source_metadata=source_metadata,
            retrieval_method="vector_search"
        )

        logger.info(f"Found {len(passages)} passages for query: {query_text[:50]}...")
        return retrieved_context

    def search_by_embedding(self, query_embedding: List[float], limit: int = 5) -> RetrievedContext:
        """
        Search for relevant passages using a pre-computed embedding

        Args:
            query_embedding: The embedding vector to search with
            limit: Maximum number of results to return

        Returns:
            RetrievedContext containing the relevant passages and metadata
        """
        # Perform vector search in Qdrant
        search_results = self.qdrant_client.search_similar(query_embedding, limit=limit)

        # Extract passages, similarity scores, and metadata
        passages = [result["text"] for result in search_results]
        similarity_scores = [result["similarity_score"] for result in search_results]
        source_metadata = [result["metadata"] for result in search_results]

        # Create and return RetrievedContext
        retrieved_context = RetrievedContext(
            passages=passages,
            similarity_scores=similarity_scores,
            source_metadata=source_metadata,
            retrieval_method="vector_search"
        )

        logger.info(f"Found {len(passages)} passages using embedding search")
        return retrieved_context

    def search_with_filters(self, query_text: str, filters: Optional[Dict[str, Any]] = None,
                           limit: int = 5) -> RetrievedContext:
        """
        Search for relevant passages with additional filters

        Args:
            query_text: The text to search for similar passages
            filters: Optional filters to apply to the search
            limit: Maximum number of results to return

        Returns:
            RetrievedContext containing the relevant passages and metadata
        """
        # This would require more advanced Qdrant filtering which is not implemented in the basic wrapper
        # For now, we'll just do a regular search and filter results afterward if needed
        retrieved_context = self.search_by_text(query_text, limit)

        # If filters are provided, apply them to the results
        if filters:
            filtered_passages = []
            filtered_scores = []
            filtered_metadata = []

            for passage, score, metadata in zip(
                retrieved_context.passages,
                retrieved_context.similarity_scores,
                retrieved_context.source_metadata
            ):
                # Apply simple filter logic - check if metadata contains filter keys
                match = True
                for key, value in filters.items():
                    if metadata.get(key) != value:
                        match = False
                        break

                if match:
                    filtered_passages.append(passage)
                    filtered_scores.append(score)
                    filtered_metadata.append(metadata)

            # Update the retrieved context with filtered results
            retrieved_context.passages = filtered_passages[:limit]
            retrieved_context.similarity_scores = filtered_scores[:limit]
            retrieved_context.source_metadata = filtered_metadata[:limit]

        logger.info(f"Found {len(retrieved_context.passages)} filtered passages for query: {query_text[:50]}...")
        return retrieved_context

    def batch_search(self, queries: List[str], limit_per_query: int = 3) -> List[RetrievedContext]:
        """
        Perform multiple searches in batch

        Args:
            queries: List of query texts
            limit_per_query: Maximum number of results per query

        Returns:
            List of RetrievedContext objects
        """
        results = []
        for query in queries:
            try:
                result = self.search_by_text(query, limit_per_query)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to search for query '{query[:30]}...': {str(e)}")
                # Return empty context for failed searches
                results.append(RetrievedContext(
                    passages=[],
                    similarity_scores=[],
                    source_metadata=[],
                    retrieval_method="vector_search"
                ))

        logger.info(f"Completed batch search for {len(queries)} queries")
        return results

    def find_most_relevant(self, query_text: str, all_passages: List[str], limit: int = 1) -> RetrievedContext:
        """
        Find the most relevant passages from a provided list of passages

        Args:
            query_text: The query text to match against
            all_passages: List of passages to search through
            limit: Maximum number of results to return

        Returns:
            RetrievedContext containing the most relevant passages
        """
        # Generate embeddings for all passages
        passage_embeddings = self.embedding_service.generate_embeddings(all_passages)
        query_embedding = self.embedding_service.generate_embedding(query_text)

        # Calculate similarity scores
        from scipy.spatial.distance import cosine
        similarity_scores = []
        for passage_embedding in passage_embeddings:
            # Calculate cosine similarity (1 - cosine distance)
            similarity = 1 - cosine(query_embedding, passage_embedding)
            similarity_scores.append(similarity)

        # Sort passages by similarity score
        scored_passages = list(zip(all_passages, similarity_scores))
        scored_passages.sort(key=lambda x: x[1], reverse=True)

        # Get top results
        top_passages = scored_passages[:limit]
        passages = [p[0] for p in top_passages]
        scores = [p[1] for p in top_passages]

        # Create metadata for these passages (simplified)
        source_metadata = [{"source": f"provided_list_{i}", "similarity": score}
                          for i, score in enumerate(scores)]

        retrieved_context = RetrievedContext(
            passages=passages,
            similarity_scores=scores,
            source_metadata=source_metadata,
            retrieval_method="provided_list_search"
        )

        logger.info(f"Found {len(passages)} most relevant passages from provided list")
        return retrieved_context


# Global instance for easy access
vector_search_service = VectorSearchService()