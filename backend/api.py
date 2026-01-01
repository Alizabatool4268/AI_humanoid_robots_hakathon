"""
API Endpoint for Backend Multi-Agent System for Book RAG Chatbot

This module implements the main API endpoint for processing user queries through the RAG pipeline.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import time
import os
from dotenv import load_dotenv

# Import our modules
from models import UserQuery as UserQueryModel
from rag_agent import rag_pipeline
from agents import multi_agent_system
from utils import AgentLogger
from validators import api_response_validator
from input_sanitizer import input_sanitizer
from rate_limiter import rate_limiter

load_dotenv()

logger = logging.getLogger(__name__)
agent_logger = AgentLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Book RAG Chatbot API", version="1.0.0")

# Request model for the API
class QueryRequest(BaseModel):
    query: str
    selected_text: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None


# Response model for the API
class QueryResponse(BaseModel):
    answer: str
    source_references: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    was_handoff: bool


# Health check endpoint
@app.get("/api/agent/health")
async def health_check():
    """
    Health check endpoint to monitor agent availability
    """
    return {
        "status": "healthy",
        "agents_available": ["triage", "query"],
        "dependencies": {
            "qdrant": "connected",  # This would be checked in a real implementation
            "cohere": "connected",  # This would be checked in a real implementation
            "gemini": "connected"   # This would be checked in a real implementation
        }
    }


# Main query endpoint
@app.post("/api/agent/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, request_ip: str = "default"):
    """
    Process a user query through the RAG pipeline

    Args:
        request: QueryRequest containing the query and optional selected text
        request_ip: IP address of the requester for rate limiting

    Returns:
        QueryResponse containing the answer and metadata
    """
    start_time = time.time()
    query_id = f"api_query_{int(start_time * 1000)}"

    # Rate limiting check
    if not rate_limiter.is_allowed(request_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {rate_limiter.requests_per_minute} requests per minute."
        )

    try:
        # Sanitize inputs
        sanitized_query = input_sanitizer.sanitize_query(request.query)
        sanitized_selected_text = input_sanitizer.sanitize_selected_text(request.selected_text) if request.selected_text else None
        sanitized_user_context = input_sanitizer.sanitize_user_context(request.user_context) if request.user_context else None

        # Validate the request after sanitization
        if not sanitized_query or not sanitized_query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Create UserQuery model instance with sanitized inputs
        user_query = UserQueryModel(
            query_text=sanitized_query,
            selected_text=sanitized_selected_text,
            user_context=sanitized_user_context
        )

        # Validate the user query
        is_valid = api_response_validator.validate_user_query(user_query)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid query format")

        agent_logger.log_query_processing(query_id, user_query.query_text, "API")

        # Process the query through the multi-agent system with triage and routing
        response = multi_agent_system.process_user_query(user_query)

        # Calculate total processing time
        response.processing_time = time.time() - start_time

        # Validate the response
        is_response_valid = api_response_validator.validate_agent_response(response)
        if not is_response_valid:
            logger.error(f"Response validation failed for query {query_id}")
            raise HTTPException(status_code=500, detail="Response validation failed")

        # Additional validation for selected text responses
        if user_query.has_selected_text():
            is_selected_text_valid = api_response_validator.validate_selected_text_response(response, user_query.selected_text)
            if not is_selected_text_valid:
                logger.warning(f"Selected text response failed validation for query {query_id}")

        agent_logger.log_response_generation(
            query_id,
            len(response.answer),
            response.confidence_score
        )

        # Format the response to match the API specification
        api_response = QueryResponse(
            answer=response.answer,
            source_references=response.source_references,
            confidence_score=response.confidence_score,
            processing_time=response.processing_time,
            was_handoff=response.was_handoff
        )

        return api_response

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error processing query {query_id}: {str(e)}")
        agent_logger.log_error(query_id, e, "API processing")

        # Return a safe error response
        return QueryResponse(
            answer="An error occurred while processing your query. Please try again.",
            source_references=[],
            confidence_score=0.0,
            processing_time=processing_time,
            was_handoff=False
        )


# Add rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Extract client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limit
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded. Maximum {rate_limiter.requests_per_minute} requests per minute."}
        )

    response = await call_next(request)
    return response


# Additional endpoint for testing purposes
@app.get("/")
async def root():
    """
    Root endpoint for basic connectivity check
    """
    return {
        "message": "Book RAG Chatbot API is running",
        "endpoints": ["/api/agent/query", "/api/agent/health"]
    }


# Add middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response


# This would be run to start the server
def start_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Helper function to start the API server

    Args:
        host: Host address to bind to
        port: Port to listen on
    """
    import uvicorn
    uvicorn.run(app, host=host, port=port)


# For development/testing purposes
if __name__ == "__main__":
    # This would start the server when running this file directly
    # In production, you'd typically run: uvicorn backend.api:app --reload
    pass