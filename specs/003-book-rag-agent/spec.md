# Feature Specification: Backend Multi-Agent System for Book RAG Chatbot

**Feature Branch**: `003-book-rag-agent`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: "Backend Multi-Agent System for Book RAG Chatbot

Target system:
Backend RAG pipeline using OpenAI Agents SDK, Cohere embeddings, Qdrant vector search, and documentation for industrial-grade structure. All backend logic must live inside backend/agent.py as the single source of truth.

Focus:
- Create a production-style backend agent that handles book-based question answering.
- Use Cohere for embeddings, OpenAI Agents for reasoning + skills, and Qdrant for retrieval.
- Follow documentation patterns for clean architecture, handler separation, and deterministic routing.

Success criteria:
- The backend agent reads user queries and selected text (if provided).
- Selected text ALWAYS overrides retrieval.
- Agent performs clean RAG retrieval using Qdrant + Cohere embeddings.
- Agent returns final answer strictly grounded in retrieved content.
- No hallucinations; every answer must reference provided or retrieved text.
- Industrial agent logic fully implemented in backend/agent.py.
- Follows OpenAI Agents sdk docs for message formatting, handoffs, and run loops.

Constraints:
- Keep all backend logic in backend/agent.py (centralized, testable entrypoint).
- Follow OpenAI Agent sdk documentation patterns for skills, handlers, and routing.
- Keep the prompt and structure short, deterministic, and modular.
- No UI logic, no frontend code, no notebook code.
- No vendor comparisons or product recommendations.
- Only perform RAG; no extra generation outside grounded text.

Backend Architecture Rules:
1. Use uv package manager , Cohere embeddings for all text chunk vectors.
2. Use Qdrant Cloud Free Tier for vector search.
3. Implement retrieval, ranking, context assembly inside agent.py.
4. Use OpenAI Agents SDK for:
   - triage → query_agent handoff
   - context injection
   - skill execution
5. Follow documentation patterns:
   - separate routing
   - isolate retrieval logic
   - minimal side effects
   - deterministic outputs

Not building:
- Full application server or frontend widget.
- Fine-grained auth system.
- Tooling outside the backend folder.
- Any code outside backend/agent.py for the agent logic.

Timeline:
- Backend agent must be operational before FastAPI and UI phases."

## Clarifications

### Session 2025-12-31

- Q: Which file should contain the agent logic: backend/agent.py or backend/agents.py? → A: Use backend/agent.py
- Q: Should the primary agent framework be OpenAI Agents SDK or Google's Gemini? → A: Use OpenAI Agents SDK as the primary agent framework
- Q: What constitutes normal load conditions for the 5-second response time requirement? → A: Up to 10 concurrent users
- Q: What is the expected volume of book content to be processed? → A: Single book up to 1000 pages
- Q: How should the system respond when no relevant content is found for a query? → A: Return "No relevant content found" message

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask questions about book content with RAG (Priority: P1)

A user wants to ask questions about specific book content and receive accurate answers grounded in the source material. The system retrieves relevant passages from the book using vector search and generates responses based on those passages, ensuring no hallucinations occur.

**Why this priority**: This is the core functionality - users need to ask questions and get accurate, source-grounded answers. This delivers the primary value of the RAG system.

**Independent Test**: Can be fully tested by providing a user query and verifying that the response is grounded in retrieved book content, with references to the source material.

**Acceptance Scenarios**:

1. **Given** user provides a question about book content, **When** system processes the query through RAG pipeline, **Then** system returns an answer based on retrieved passages from the book
2. **Given** user provides a question that requires information from multiple book sections, **When** system performs retrieval and ranking, **Then** system synthesizes information from relevant passages to form a coherent answer

---

### User Story 2 - Override retrieval with selected text (Priority: P2)

A user wants to provide specific text they've selected from a book and have the system answer questions based solely on that text, bypassing the general retrieval process.

**Why this priority**: This provides users with more control over the context used for answering, allowing them to focus on specific passages they're interested in.

**Independent Test**: Can be fully tested by providing selected text along with a question and verifying that the response is based only on the provided text, not on general retrieval.

**Acceptance Scenarios**:

1. **Given** user provides both a question and selected text, **When** system processes the request, **Then** system uses only the selected text to generate the answer, ignoring general retrieval
2. **Given** user provides selected text that contradicts general book content, **When** system answers the question, **Then** system prioritizes the selected text over retrieved passages

---

### User Story 3 - Multi-agent processing with routing (Priority: P3)

The system uses multiple agents with different responsibilities (triage, query handling, context injection) that work together to process user requests efficiently.

**Why this priority**: This enables sophisticated processing and ensures the system can handle different types of queries appropriately through specialized agents.

**Independent Test**: Can be tested by verifying that different types of queries are routed to appropriate agents and processed according to their specialized functions.

**Acceptance Scenarios**:

1. **Given** user submits a complex query requiring multiple processing steps, **When** system routes through different agents, **Then** query is processed by appropriate specialized agents in sequence

---

### Edge Cases

- When no relevant content is found in the book for a given query, the system returns "No relevant content found" message
- How does the system handle queries that span multiple books or documents?
- What occurs when the selected text is too short to provide meaningful answers?
- How does the system handle malformed or ambiguous queries?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept user queries about book content and return answers grounded in retrieved text
- **FR-002**: System MUST use vector embeddings for converting text to numerical representations for similarity matching
- **FR-003**: System MUST use vector search for retrieving relevant book passages based on query similarity
- **FR-004**: System MUST use multi-agent architecture for processing and routing user requests
- **FR-005**: System MUST prioritize user-provided selected text over general retrieval when both are available
- **FR-006**: System MUST prevent hallucinations by ensuring all answers reference provided or retrieved text
- **FR-007**: System MUST implement retrieval, ranking, and context assembly for question answering
- **FR-008**: System MUST follow deterministic routing patterns for agent handoffs
- **FR-009**: System MUST maintain all backend logic within a single centralized file for testability
- **FR-010**: System MUST handle query triage and route to appropriate specialized agents

### Key Entities *(include if feature involves data)*

- **User Query**: The question or request submitted by the user, containing the text they want answered
- **Book Content**: The source material stored in vector format in Qdrant, used for retrieval
- **Retrieved Context**: Relevant passages retrieved from book content based on query similarity
- **Selected Text**: Specific text provided by user that overrides general retrieval
- **Agent Response**: The final answer generated by the system, grounded in retrieved or provided content
- **Vector Embeddings**: Numerical representations of text created using Cohere embeddings

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users receive accurate answers to book-related questions that are strictly grounded in retrieved content with no hallucinations
- **SC-002**: System processes user queries and returns answers within 5 seconds under normal load conditions (up to 10 concurrent users)
- **SC-003**: 95% of generated responses contain references to specific retrieved or provided text passages
- **SC-004**: System successfully handles 90% of diverse book-related queries with meaningful, accurate responses
- **SC-005**: Multi-agent routing correctly directs 98% of queries to appropriate specialized agents