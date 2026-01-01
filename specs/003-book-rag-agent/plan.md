# Implementation Plan: Backend Multi-Agent System for Book RAG Chatbot

**Branch**: `003-book-rag-agent` | **Date**: 2025-12-31 | **Spec**: [link](specs/003-book-rag-agent/spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Production-ready backend agent that routes book-related queries via a triage agent to a query agent for RAG responses, ensuring deterministic, grounded answers. The system uses a multi-agent architecture with Gemini for classification/triage, Cohere embeddings for vector search in Qdrant, and follows OpenAI Agents SDK best practices. All backend logic resides in backend/agents.py with selected text always overriding RAG retrieval.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: OpenAI Agents SDK, Cohere API, Qdrant vector database, Google Generative AI (Gemini)
**Storage**: Qdrant Cloud (vector storage), with book content embeddings
**Testing**: pytest for unit tests, mock queries for agent testing
**Target Platform**: Linux server (backend service)
**Project Type**: Backend service
**Performance Goals**: <5 seconds response time for queries, 95% accuracy in book-related query detection
**Constraints**: All logic in single backend/agents.py file, minimal compute usage, free tier services
**Scale/Scope**: Single backend service handling book-related queries with RAG capabilities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Precision in Technical Robotics and AI Concepts)**: ✅ Satisfied - Multi-agent RAG system follows established AI patterns
- **Principle IV (Simple, Easy to Understand, Accurate, and Simple Content)**: ✅ Satisfied - Agent responses will be grounded in book content
- **Principle VIII (RAG Chatbot Scope)**: ✅ Satisfied - Directly implements RAG chatbot answering questions based on book content
- **Principle IX (LLM Reasoning Restriction)**: ✅ Satisfied - Responses restricted to book content + selected text
- **Principle X (Minimal Compute and Efficient Content)**: ✅ Satisfied - Using free tier services (Qdrant Cloud Free Tier, Cohere embeddings)

## Project Structure

### Documentation (this feature)

```text
specs/003-book-rag-agent/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── agents.py            # Main multi-agent system implementation
├── requirements.txt     # Dependencies (OpenAI Agents SDK, Cohere, Qdrant, Google Generative AI)
└── tests/
    └── test_agents.py   # Unit tests for agent functionality
```

**Structure Decision**: Backend service structure chosen with all agent logic centralized in backend/agents.py as required by specification

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |