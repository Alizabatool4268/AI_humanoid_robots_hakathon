# Tasks: Backend Multi-Agent System for Book RAG Chatbot

**Feature**: 003-book-rag-agent
**Created**: 2025-12-31
**Based on**: specs/003-book-rag-agent/spec.md, plan.md, data-model.md, contracts/agent-api.yaml

## Overview

Implementation of a Backend Multi-Agent System for Book RAG Chatbot using OpenAI Agents SDK with Gemini for triage, Cohere embeddings with Qdrant for RAG, ensuring deterministic, grounded answers.

## Dependencies

- User Story 2 (US2) requires foundational components from User Story 1 (US1) for selected text override functionality
- User Story 3 (US3) requires foundational agent framework from User Story 1 (US1) for multi-agent routing

## Parallel Execution Examples

- API endpoint implementation can run in parallel with agent logic implementation
- Qdrant setup can run in parallel with Cohere integration
- Testing tasks can run in parallel with implementation tasks

## Dependency Graph

```
T001,T002,T003,T004 (Setup)
    ↓
T005,T006,T007,T008,T009,T010 (Foundational)
    ↓
T011,T012,T013,T014,T015,T016,T017,T018,T019,T020 (US1 - Core RAG)
    ↓
T021,T022,T023,T024,T025,T026,T027,T028 (US2 - Selected Text Override)
    ↓
T029,T030,T031,T032,T033,T034,T035,T036,T037,T038,T039 (US3 - Multi-Agent Routing)
    ↓
T040,T041,T042,T043,T044,T045,T046,T047,T048,T049 (Polish & Cross-Cutting)
```

### User Story Dependencies:
- US2 (Selected Text Override) depends on foundational components from US1
- US3 (Multi-Agent Routing) depends on core agent framework from US1 and US2

## Implementation Strategy

1. **MVP Scope**: Start with US1 (basic RAG functionality) to establish core capabilities
2. **Incremental Delivery**: Add US2 (selected text override) and US3 (multi-agent routing) in subsequent phases
3. **Foundation First**: Complete setup and foundational tasks before user story-specific implementation

---

## Phase 1: Setup

- [X] T001 Create backend directory structure with agents.py, requirements.txt, and tests directory
- [X] T002 Set up requirements.txt with OpenAI Agents SDK, Cohere, Qdrant, Google Generative AI, python-dotenv dependencies
- [X] T003 Create initial .env file structure for API keys (Qdrant, Cohere, Gemini, OpenAI)
- [X] T004 Initialize test directory with test_agents.py file structure

## Phase 2: Foundational Components

- [X] T005 [P] Create Qdrant client wrapper in backend/qdrant_client.py for vector operations
- [X] T006 [P] Create Cohere embedding service in backend/embedding_service.py for text vectorization
- [X] T007 [P] Create Gemini service wrapper in backend/gemini_service.py for classification and generation
- [X] T008 Create data models in backend/models.py based on data-model.md (UserQuery, AgentResponse, RetrievedContext, AgentState)
- [X] T009 Create API response validators in backend/validators.py to ensure grounding requirements
- [X] T010 Set up logging and monitoring utilities in backend/utils.py for agent operations

## Phase 3: [US1] Ask questions about book content with RAG

**Goal**: Enable users to ask questions about book content and receive accurate answers grounded in source material using RAG pipeline.

**Independent Test**: Can be fully tested by providing a user query and verifying that the response is grounded in retrieved book content, with references to the source material.

**Tasks**:

- [X] T011 [P] [US1] Implement Qdrant collection setup for book content embeddings
- [X] T012 [P] [US1] Create embedding ingestion pipeline to store book content in Qdrant
- [X] T013 [P] [US1] Implement vector search functionality in backend/search_service.py
- [X] T014 [P] [US1] Create response generation service using Gemini for grounded answers
- [X] T015 [US1] Implement core RAG pipeline in backend/rag_agent.py that connects search and generation
- [X] T016 [US1] Add source reference tracking to ensure all responses include proper citations
- [X] T017 [US1] Implement hallucination prevention by validating all responses against source material
- [X] T018 [US1] Create basic API endpoint POST /api/agent/query for direct RAG requests
- [X] T019 [US1] Add response time monitoring to ensure <5 seconds performance
- [X] T020 [US1] Write unit tests for RAG functionality in tests/test_rag.py

## Phase 4: [US2] Override retrieval with selected text

**Goal**: Allow users to provide specific text they've selected from a book and have the system answer questions based solely on that text, bypassing general retrieval.

**Independent Test**: Can be fully tested by providing selected text along with a question and verifying that the response is based only on the provided text, not on general retrieval.

**Tasks**:

- [X] T021 [P] [US2] Enhance UserQuery model to properly handle selected_text field with validation
- [X] T022 [P] [US2] Create selected text processing service in backend/selected_text_service.py
- [X] T023 [US2] Modify RAG pipeline to prioritize selected_text when provided (FR-005)
- [X] T024 [US2] Update response generation to use selected text as primary context when available
- [X] T025 [US2] Add validation to ensure selected text responses contain proper source references
- [X] T026 [US2] Update API endpoint to accept and process selected_text parameter
- [X] T027 [US2] Write unit tests for selected text override functionality in tests/test_selected_text.py
- [ ] T028 [US2] Add integration tests to verify selected text always overrides retrieval

## Phase 5: [US3] Multi-agent processing with routing

**Goal**: Implement multi-agent system with triage and query agents that work together to process user requests efficiently.

**Independent Test**: Can be tested by verifying that different types of queries are routed to appropriate agents and processed according to their specialized functions.

**Tasks**:

- [X] T029 [P] [US3] Create triage agent class in backend/agents.py for query classification
- [X] T030 [P] [US3] Implement Gemini-based query classification in triage agent
- [X] T031 [P] [US3] Create query agent class in backend/agents.py for RAG processing
- [X] T032 [US3] Implement deterministic agent handoff mechanism between triage and query agents
- [X] T033 [US3] Add agent state management to track current processing agent
- [X] T034 [US3] Create agent communication protocol based on contracts/agent-api.yaml
- [X] T035 [US3] Update main API endpoint to use multi-agent routing instead of direct RAG
- [X] T036 [US3] Add health check endpoint GET /api/agent/health to monitor agent availability
- [X] T037 [US3] Implement error handling for agent communication failures
- [X] T038 [US3] Write unit tests for agent routing logic in tests/test_agents_routing.py
- [ ] T039 [US3] Add integration tests to verify 98% query routing accuracy (SC-005)

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T040 Implement comprehensive input sanitization to prevent injection attacks
- [X] T041 Add rate limiting middleware to API endpoints (100 requests/min per IP)
- [X] T042 Implement proper error handling with standardized error response format
- [X] T043 Add performance monitoring and logging for all agent operations
- [ ] T044 Create comprehensive test suite covering all user stories
- [ ] T045 Add documentation comments to all major functions and classes
- [ ] T046 Perform final integration testing to ensure 95% response grounding (SC-003)
- [ ] T047 Optimize response times to meet <5 second requirement (SC-002)
- [ ] T048 Conduct end-to-end testing with sample book content
- [ ] T049 Final code review and refactoring for maintainability