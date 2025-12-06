---
id: 2
title: Create Project Constitution for AI-Native Textbook
stage: constitution
date: 2025-12-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: unknown
command: /sp.constitution
labels: ["constitution", "project-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

 Project: AI-Native Textbook on Physical AI & Humanoid Robotics with integrated RAG chatbot and personalization features.
Core Principles:
Precision in technical robotics and AI concepts
Accessibility for students with varying software/hardware backgrounds
The book will contain the following chapters
1.ROS 2 fundamentals (nodes, topics, services, URDF)
2.Gazebo simulation, physics, Unity visualization
3.NVIDIA Isaac Sim, Isaac ROS, Nav2
4.Vision-Language-Action robotics
5.Conversational robotics (Whisper + LLM planning)
6.Capstone: Autonomous humanoid robot executing spoken tasks
UI must be clean minimal and fast and modern
Content must be simple, easy to understand, accurate and simple
Key Standards:
All chapters stored as Markdown and programmatically retrievable


Roman Urdu translation available for every chapter via toggle


User highlights persist via browser localStorage


RAG chatbot answers questions based on entire book or user-selected text


LLM reasoning restricted only to book content + selected text
Minimal compute usage
Keep chapter size small and clean
Light weight embeddings and use free tiers


Technical Requirements:
Frontend: Docusaurus, chapter personalization button


Backend: FastAPI + Qdrant Cloud + Neon Postgres


Auth: Better-Auth for signup/signin and background-based content personalization


Claude Code Subagents + Skills for modular, reusable automation


Constraints:
Textbook must remain concise, technically accurate, and agent-friendly


All features must function with static Markdown files


Book deployable on GitHub Pages


Minimal compute usage
Keep chapter size small and clean
Light weight embeddings and use free tiers


Success Criteria:
Book fully published and browsable


RAG chatbot correctly answers from book + selected text only


Roman Urdu toggle works reliably for all chapters


LocalStorage highlight system persists across sessions


Personalized chapter generation functional for logged-in users


Codebase structured for reproducible AI-native development

## Response snapshot

The project constitution has been created at `.specify/memory/constitution.md`, versioned at 1.0.0. This is an initial major version release as it defines the core principles and structure for the "AI-Native Textbook on Physical AI & Humanoid Robotics" project. No manual follow-up is required for other templates at this time, as they align with the new constitution.

Suggested commit message:
`docs: create constitution v1.0.0 (initial principles + project definition)`

## Outcome

- ✅ Impact: Successfully created and updated the project constitution.
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: none
- 🧠 Reflection: Successfully parsed user input to create the initial project constitution and handled fallback for PHR creation script.

## Evaluation notes (flywheel)

- Failure modes observed: create-phr.sh script not found, fell back to agent-native PHR creation.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Ensure create-phr.sh script is available or improve agent-native PHR creation robustness.
