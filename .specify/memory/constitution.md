<!-- Sync Impact Report:
Version change: 0.0.0 -> 1.0.0
Modified principles: All principles added as this is the initial constitution.
Added sections: Technical Requirements, Constraints.
Removed sections: None.
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated (no changes needed)
- .specify/templates/spec-template.md: ✅ updated (no changes needed)
- .specify/templates/tasks-template.md: ✅ updated (no changes needed)
Follow-up TODOs: None.
-->
# AI-Native Textbook on Physical AI & Humanoid Robotics Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### I. Precision in Technical Robotics and AI Concepts
Precision in technical robotics and AI concepts

### II. Accessibility for Students
Accessibility for students with varying software/hardware backgrounds

### III. Clean, Minimal, Fast, and Modern UI
UI must be clean minimal and fast and modern

### IV. Simple, Easy to Understand, Accurate, and Simple Content
Content must be simple, easy to understand, accurate and simple

### V. Markdown Chapter Storage
All chapters stored as Markdown and programmatically retrievable

### VI. Roman Urdu Translation
Roman Urdu translation available for every chapter via toggle

### VII. User Highlights Persistence
User highlights persist via browser localStorage

### VIII. RAG Chatbot Scope
RAG chatbot answers questions based on entire book or user-selected text

### IX. LLM Reasoning Restriction
LLM reasoning restricted only to book content + selected text

### X. Minimal Compute and Efficient Content
Minimal compute usage, Keep chapter size small and clean, Light weight embeddings and use free tiers

## Technical Requirements
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

- Frontend: Docusaurus, chapter personalization button
- Backend: FastAPI + Qdrant Cloud + Neon Postgres
- Auth: Better-Auth for signup/signin and background-based content personalization
- Claude Code Subagents + Skills for modular, reusable automation

## Constraints
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

- Textbook must remain concise, technically accurate, and agent-friendly
- All features must function with static Markdown files
- Book deployable on GitHub Pages
- Minimal compute usage
- Keep chapter size small and clean
- Light weight embeddings and use free tiers

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

- This constitution supersedes all other project practices.
- Amendments require documentation, approval, and a migration plan.
- All PRs/reviews must verify compliance.
- Complexity must be justified.

**Version**: 1.0.0 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-05
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
