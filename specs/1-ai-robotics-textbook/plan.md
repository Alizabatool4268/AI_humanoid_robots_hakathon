# Implementation Plan: AI-Native Textbook on Physical AI & Humanoid Robotics

**Branch**: `1-ai-robotics-textbook` | **Date**: 2025-12-05 | **Spec**: specs/1-ai-robotics-textbook/spec.md
**Input**: Feature specification from `/specs/1-ai-robotics-textbook/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Objective: Plan the creation of a simple, clean, English-only AI-Native textbook on Physical AI & Humanoid Robotics with 6 chapters.
Architecture Sketch: Docusaurus static book with auto-sidebar. Six Markdown chapters stored in `/docs`. Flow: Research → Draft → Review → Final Markdown.

## Technical Context

**Language/Version**: TypeScript, React 18, Python (for ROS 2 and backend concepts)
**Primary Dependencies**: Docusaurus 3.x
**Storage**: Markdown files for chapters
**Testing**: Unit testing for React components (Jest, React Testing Library), Content validation (MDX syntax, frontmatter, broken links), E2E testing (Playwright)
**Target Platform**: Web (Docusaurus for frontend, GitHub Pages for deployment)
**Project Type**: Web application (Docusaurus frontend)
**Performance Goals**: Fast and modern UI, easy to navigate and and read
**Constraints**: English canonical source, Markdown-only chapter storage, maintain technical accuracy for robotics and AI, deployable on GitHub Pages, minimal compute usage, keep chapter size small and clean, light weight embeddings and use free tiers.
**Scale/Scope**: 6 chapters, each with a 5-part structure (short intro, core concepts, simple example/scenario, relevance to humanoid robotics, short summary).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Precision in Technical Robotics and AI Concepts**: Adhered to by maintaining technical accuracy (FR-005 in spec).
- [x] **II. Accessibility for Students**: Adhered to by making content beginner-friendly (FR-002 in spec).
- [x] **III. Clean, Minimal, Fast, and Modern UI**: Adhered to by using Docusaurus and ensuring good navigation (FR-001, FR-003, FR-006, FR-007 in spec).
- [x] **IV. Simple, Easy to Understand, Accurate, and Simple Content**: Adhered to by FR-002 and FR-005 in spec.
- [x] **V. Markdown Chapter Storage**: Adhered to by FR-004 in spec.
- [ ] **VI. Roman Urdu Translation**: Not Applicable (explicitly "Not building" in spec and user input).
- [ ] **VII. User Highlights Persistence**: Not Applicable (explicitly "Not building" in spec and user input).
- [ ] **VIII. RAG Chatbot Scope**: Not Applicable (explicitly "Not building" in spec and user input).
- [ ] **IX. LLM Reasoning Restriction**: Not Applicable (explicitly "Not building" in spec and user input).
- [x] **X. Minimal Compute and Efficient Content**: Adhered to by minimal compute usage constraint in spec and user input.

## Project Structure

### Documentation (this feature)

```text
specs/1-ai-robotics-textbook/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Option 2: Web application (when "frontend" + "backend" detected)
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── theme/
│   └── utils/
└── docs/
    ├── intro.md
    ├── 1-ros2-fundamentals/
    ├── 2-gazebo-unity/
    ├── 3-nvidia-isaac/
    ├── 4-vision-language-action/
    ├── 5-conversational-robotics/
    └── 6-capstone/
```

**Structure Decision**: The project will follow a web application structure, focusing on the Docusaurus frontend, with content organized within the `docs/` directory. The backend components (FastAPI, Qdrant, Neon Postgres, Better-Auth) mentioned in the constitution's technical requirements are currently out of scope per the spec's "Not building" section and the user's explicit "Not building" section in this plan, and will not be reflected in this initial `plan.md`'s source code structure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
|           |            |                                     |
