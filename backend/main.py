"""Main RAG ingestion pipeline execution"""

import asyncio
from typing import List, Dict, Any
from src.crawler import get_all_urls
from src.extractor import extract_text_from_url
from src.chunker import chunk_text
from src.embedder import embed
from src.storage import create_collection, save_chunks_to_qdrant
from src.config.settings import Settings
from src.logger import pipeline_logger
import time


async def main():
    """
    Main pipeline execution: crawl → extract → chunk → embed → store
    """
    start_time = time.time()
    pipeline_logger.info("Starting RAG ingestion pipeline...")

    settings = Settings()
    settings.validate()

    # Phase 1: Crawl website
    pipeline_logger.info("Phase 1: Crawling website...")
    urls = get_all_urls(
        base_url=settings.WEBSITE_URL,
        sitemap_url=settings.SITEMAP_URL
    )
    pipeline_logger.info(f"Discovered {len(urls)} URLs")

    # Phase 2: Extract content from each URL
    pipeline_logger.info("Phase 2: Extracting content...")
    all_chunks = []
    processed_count = 0
    error_count = 0

    for url in urls:
        try:
            content_data = extract_text_from_url(url)
            chunks = chunk_text(
                content_data["content"],
                url,
                content_data["title"],
                " > ".join(content_data["section_hierarchy"]) if content_data["section_hierarchy"] else ""
            )
            all_chunks.extend(chunks)
            processed_count += 1

            if processed_count % 10 == 0:  # Log progress every 10 URLs
                pipeline_logger.info(f"Processed {processed_count}/{len(urls)} URLs...")

        except Exception as e:
            pipeline_logger.error(f"Error processing {url}: {e}")
            error_count += 1
            continue

    pipeline_logger.info(f"Created {len(all_chunks)} text chunks from {processed_count} URLs ({error_count} errors)")

    if not all_chunks:
        pipeline_logger.error("No chunks were created. Pipeline terminated.")
        return

    # Phase 3: Generate embeddings
    pipeline_logger.info("Phase 3: Generating embeddings...")
    try:
        chunks_with_embeddings = embed(all_chunks)
        pipeline_logger.info(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
    except Exception as e:
        pipeline_logger.error(f"Error during embedding generation: {e}")
        return

    if not chunks_with_embeddings:
        pipeline_logger.error("No chunks with embeddings were created. Pipeline terminated.")
        return

    # Phase 4: Create Qdrant collection and store vectors
    pipeline_logger.info("Phase 4: Creating Qdrant collection and storing vectors...")
    collection_name = settings.COLLECTION_NAME
    success = create_collection(collection_name)

    if not success:
        pipeline_logger.error(f"Failed to create collection '{collection_name}'. Pipeline terminated.")
        return

    # Save chunks to Qdrant
    success_count = save_chunks_to_qdrant(chunks_with_embeddings, collection_name)

    end_time = time.time()
    duration = end_time - start_time

    pipeline_logger.info(f"Pipeline completed successfully!")
    pipeline_logger.info(f"Summary: {success_count} of {len(chunks_with_embeddings)} chunks stored in Qdrant collection '{collection_name}'")
    pipeline_logger.info(f"Total execution time: {duration:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
