# Research: Backend Multi-Agent System for Book RAG Chatbot

**Feature**: 003-book-rag-agent
**Date**: 2025-12-31

## Overview

This research document addresses the technical implementation details for the Backend Multi-Agent System for Book RAG Chatbot, focusing on the multi-agent architecture using OpenAI Agents SDK with Gemini for triage and Cohere embeddings with Qdrant for RAG.

## Technology Decisions

### 1. Multi-Agent Architecture with OpenAI Agents SDK

**Decision**: Implement triage and query agents using OpenAI Agents SDK
**Rationale**: The OpenAI Agents SDK provides a well-documented framework for creating multi-agent systems with clear handoff mechanisms. It supports the required routing patterns and deterministic outputs.
**Alternatives considered**:
- Custom agent framework: More development time, less established
- LangChain agents: Different architecture than specified

### 2. Intent Classification with Gemini

**Decision**: Use Google's Gemini model for intent classification in the triage agent
**Rationale**: The user specifically requested Gemini for classification/triage. Gemini is well-suited for text classification tasks and integrates well with the overall architecture.
**Alternatives considered**:
- OpenAI GPT models: Would create inconsistency with user requirements
- Cohere models: Not specifically requested for classification

### 3. Vector Embeddings with Cohere

**Decision**: Use Cohere for generating vector embeddings for book content
**Rationale**: Cohere embeddings are known for their quality in semantic search tasks. The user specifically mentioned Cohere embeddings in both the original spec and the planning request.
**Alternatives considered**:
- OpenAI embeddings: Would create inconsistency with requirements
- Sentence Transformers: Self-hosted option but more complex setup

### 4. Vector Database with Qdrant

**Decision**: Use Qdrant Cloud for vector storage and retrieval
**Rationale**: Qdrant is specifically mentioned in the requirements and offers good performance for semantic search. The free tier meets the minimal compute requirement.
**Alternatives considered**:
- Pinecone: Commercial alternative but not specified in requirements
- Chroma: Open source but less scalable than Qdrant

### 5. Centralized Agent Logic

**Decision**: Implement all backend logic in backend/agents.py as required
**Rationale**: The specification explicitly requires all backend logic to be in a single file for testability and centralized control.
**Alternatives considered**:
- Modular structure: Would violate the single file constraint

## Implementation Patterns

### Agent Handoff Pattern

The triage agent will classify user queries and hand off book-related queries to the query agent. This pattern ensures:
- Deterministic routing based on query intent
- Specialized processing for different query types
- Clear separation of concerns between agents

### RAG Implementation Pattern

The query agent will:
1. Accept user queries and optional selected text
2. If selected text is provided, use it as the primary context (always overrides retrieval)
3. If no selected text, perform vector search in Qdrant using Cohere embeddings
4. Assemble context from retrieved passages
5. Generate grounded responses using the Gemini model
6. Ensure all responses reference the provided or retrieved text

### Context Management

The system will manage context by:
- Prioritizing user-provided selected text over retrieved content
- Maintaining source references for all generated responses
- Ensuring no hallucinations by grounding all answers in source material

## Dependencies and Setup

### Required Dependencies
- openai-agents: For multi-agent architecture
- cohere: For vector embeddings
- qdrant-client: For vector database operations
- google-generativeai: For Gemini integration
- python-dotenv: For environment variable management

### Setup Requirements
- Qdrant Cloud account with collection for book embeddings
- Cohere API key for embedding generation
- Google AI API key for Gemini access
- OpenAI API key for agents framework (if required)

## Risk Assessment

### Technical Risks
1. **API Availability**: Relying on multiple external APIs (Cohere, Qdrant, Gemini) could introduce dependency risks
   - Mitigation: Implement proper error handling and fallbacks

2. **Response Time**: Multiple API calls in the chain could impact response time
   - Mitigation: Optimize embedding retrieval and implement caching where appropriate

3. **Consistency**: Using multiple LLM providers (Gemini for triage, potentially others for RAG) could create consistency issues
   - Mitigation: Ensure clear output formatting standards

### Implementation Risks
1. **Complexity**: Multi-agent system with external dependencies increases complexity
   - Mitigation: Follow established patterns and implement comprehensive testing

2. **Maintenance**: Multiple external services require ongoing key management
   - Mitigation: Use environment variable configuration and proper secrets management