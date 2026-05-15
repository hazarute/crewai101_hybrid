"""
tasks/task_definitions.py — Task factory functions for the Hybrid AI Agency.

Pipeline:
  Project Architect → Python Backend → TypeScript Frontend →
  QA Engineer → DevOps Engineer → Technical Writer

Each agent is directed to write real project files to disk via FileWriterTool.
If an agent cannot use the tool, it must emit files using the === FILE: === marker
format so utils/file_extractor.py can extract them after the crew run.

File marker format (fallback):
  === FILE: projects/<slug>/relative/path ===
  ```lang
  <content>
  ```
  === END FILE ===
"""

from crewai import Task

from agents.project_architect import project_architect
from agents.backend_developer import backend_developer
from agents.frontend_developer import frontend_developer
from agents.test_engineer import test_engineer
from agents.devops_agent import devops_agent
from agents.tech_writer import tech_writer
from agents.team_leader import team_leader
from agents.code_reviewer import code_reviewer


_FILE_FORMAT_HELP = (
    "If FileWriterTool is unavailable, embed each file using this EXACT format:\n"
    "=== FILE: projects/<slug>/relative/path/to/file ===\n"
    "```lang\n"
    "<file content>\n"
    "```\n"
    "=== END FILE ==="
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Architecture
# ─────────────────────────────────────────────────────────────────────────────

def create_architecture_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Analyse the following feature request and design the complete project:\n\n"
            f"{feature_description}\n\n"
            "## Your responsibilities\n"
            "1. Choose a concise project slug: lowercase kebab-case "
            "(e.g. reverse-api, todo-app, image-resizer).\n"
            "2. Confirm the full tech stack:\n"
            "   - Backend: FastAPI + Pydantic v2 + SQLModel + Alembic + Python 3.12\n"
            "   - Frontend: Next.js 14 App Router + TypeScript 5 + Tailwind CSS + Zod\n"
            "3. Define every API endpoint: HTTP method, path, request body schema, "
            "response schema, and HTTP status codes.\n"
            "4. Define every data model (Pydantic schema + SQLModel table).\n"
            "5. Define the complete folder structure.\n"
            "6. Write these files using FileWriterTool:\n"
            "   a) projects/<slug>/ARCHITECTURE.md "
            "(full design doc: API contract, models, folder tree, tech rationale)\n"
            "   b) projects/<slug>/backend/pyproject.toml "
            "(Python deps, pytest config, ruff config)\n"
            "   c) projects/<slug>/frontend/package.json "
            "(Node deps, dev scripts)\n"
            "   d) projects/<slug>/.gitignore\n"
            "   e) projects/<slug>/.env.example\n\n"
            f"{_FILE_FORMAT_HELP}\n\n"
            "## MANDATORY — your Final Answer MUST begin with exactly:\n"
            "PROJECT_SLUG: <the-slug-you-chose>\n"
            "followed by a summary of all files written and the complete API contract."
        ),
        expected_output=(
            "First line: `PROJECT_SLUG: <slug>`\n"
            "Then:\n"
            "- List of all files written to disk\n"
            "- Complete API contract (all endpoints with schemas)\n"
            "- Data model definitions\n"
            "- Technology decisions with rationale"
        ),
        agent=project_architect,
        output_file="output/00_architecture.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Backend
# ─────────────────────────────────────────────────────────────────────────────

def create_backend_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Implement the complete Python backend for:\n\n{feature_description}\n\n"
            "The architecture document is in your context. "
            "Extract PROJECT_SLUG from the first line of the architecture output "
            "(format: `PROJECT_SLUG: <slug>`) and use it for all file paths.\n\n"
            "## Required files — write ALL using FileWriterTool:\n"
            "- projects/<slug>/backend/app/__init__.py\n"
            "- projects/<slug>/backend/app/main.py        "
            "(FastAPI app factory, CORS middleware, lifespan)\n"
            "- projects/<slug>/backend/app/config.py      "
            "(pydantic-settings BaseSettings)\n"
            "- projects/<slug>/backend/app/models.py      "
            "(SQLModel tables + Pydantic request/response schemas)\n"
            "- projects/<slug>/backend/app/database.py    "
            "(async engine, get_session dependency)\n"
            "- projects/<slug>/backend/app/routes/__init__.py\n"
            "- projects/<slug>/backend/app/routes/api.py  "
            "(all endpoints matching the architecture contract)\n"
            "- projects/<slug>/backend/pyproject.toml     (if not already written)\n"
            "- projects/<slug>/backend/.env.example\n\n"
            "## Implementation requirements\n"
            "- FastAPI with async endpoints and proper HTTP status codes\n"
            "- Pydantic v2 input validation on every request body and query param\n"
            "- CORS middleware allowing the frontend origin (localhost:3000 + production)\n"
            "- OWASP Top 10: no secrets in code, parameterised SQL, validated inputs\n"
            "- JSON error responses with `detail` field on all 4xx/5xx responses\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All backend source files written to projects/<slug>/backend/. "
            "Final Answer lists every file created and the API endpoints implemented."
        ),
        agent=backend_developer,
        output_file="output/01_backend.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Frontend
# ─────────────────────────────────────────────────────────────────────────────

def create_frontend_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Implement the complete TypeScript frontend for:\n\n{feature_description}\n\n"
            "The architecture and backend implementation are in your context. "
            "Extract PROJECT_SLUG from the architecture output and use it for all paths.\n\n"
            "## Required files — write ALL using FileWriterTool:\n"
            "- projects/<slug>/frontend/src/app/layout.tsx\n"
            "- projects/<slug>/frontend/src/app/page.tsx\n"
            "- projects/<slug>/frontend/src/app/globals.css\n"
            "- projects/<slug>/frontend/src/components/<FeatureName>.tsx "
            "(main feature component)\n"
            "- projects/<slug>/frontend/src/lib/api.ts     "
            "(typed API client, all fetch calls)\n"
            "- projects/<slug>/frontend/src/lib/types.ts   "
            "(Zod schemas mirroring backend Pydantic models)\n"
            "- projects/<slug>/frontend/next.config.ts     "
            "(/api/* proxied to http://localhost:8000)\n"
            "- projects/<slug>/frontend/tailwind.config.ts\n"
            "- projects/<slug>/frontend/tsconfig.json      (strict mode enabled)\n"
            "- projects/<slug>/frontend/package.json       (if not already written)\n\n"
            "## Implementation requirements\n"
            "- Next.js 14 App Router + TypeScript strict mode\n"
            "- Zod schemas that mirror the backend Pydantic models exactly\n"
            "- Handle loading, error, and empty states in every UI component\n"
            "- Accessible: semantic HTML, aria labels where helpful\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All frontend source files written to projects/<slug>/frontend/. "
            "Final Answer lists every file created."
        ),
        agent=frontend_developer,
        output_file="output/02_frontend.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Testing
# ─────────────────────────────────────────────────────────────────────────────

def create_testing_task() -> Task:
    return Task(
        description=(
            "Write comprehensive test suites for both the Python backend and the "
            "TypeScript frontend.\n"
            "The full implementation is in your context. "
            "Extract PROJECT_SLUG from the architecture output.\n\n"
            "## Backend tests (pytest) — write to projects/<slug>/backend/tests/:\n"
            "- tests/__init__.py\n"
            "- tests/conftest.py  "
            "(pytest fixtures: async test client, in-memory SQLite DB)\n"
            "- tests/test_api.py  "
            "(≥ 3 test cases per endpoint: 200 happy path, 422 validation, edge case)\n\n"
            "## Frontend tests (Vitest) — write to projects/<slug>/frontend/__tests__/:\n"
            "- __tests__/setup.ts           (Vitest + Testing Library + happy-dom config)\n"
            "- __tests__/<Component>.test.tsx  "
            "(render, user interaction, API mock via MSW)\n\n"
            "## Requirements\n"
            "- Use httpx.AsyncClient for backend endpoint tests\n"
            "- Use @testing-library/user-event for frontend interaction tests\n"
            "- Test all component states: initial render, loading, success, error\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All test files written to disk. "
            "Final Answer: list of test files + summary of coverage scope."
        ),
        agent=test_engineer,
        output_file="output/03_tests.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. DevOps
# ─────────────────────────────────────────────────────────────────────────────

def create_devops_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Deliver the complete DevOps configuration for:\n\n{feature_description}\n\n"
            "The full implementation is in your context. "
            "Extract PROJECT_SLUG from the architecture output.\n\n"
            "## Required files — write ALL using FileWriterTool:\n"
            "- projects/<slug>/backend/Dockerfile          "
            "(multi-stage: builder + runtime, non-root user, HEALTHCHECK)\n"
            "- projects/<slug>/frontend/Dockerfile         "
            "(multi-stage: node builder + nginx runtime)\n"
            "- projects/<slug>/docker-compose.yml          "
            "(backend + frontend + optional db with health checks)\n"
            "- projects/<slug>/.github/workflows/ci.yml    "
            "(lint → test → build → push; deploy only on main branch)\n"
            "- projects/<slug>/smoke_test.sh               "
            "(curl-based checks for all critical endpoints)\n"
            "- projects/<slug>/.env.example                "
            "(all required env vars with descriptions)\n\n"
            "## Requirements\n"
            "- Docker multi-stage builds with layer caching optimisation\n"
            "- Non-root user in every container image\n"
            "- CI runs tests before building Docker images\n"
            "- smoke_test.sh verifies at least one backend and one frontend URL\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All DevOps files written to disk. "
            "Final Answer: file list + deployment architecture summary."
        ),
        agent=devops_agent,
        output_file="output/04_devops.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6. Documentation
# ─────────────────────────────────────────────────────────────────────────────

def create_documentation_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Write complete documentation for the project:\n\n{feature_description}\n\n"
            "The full implementation is in your context. "
            "Extract PROJECT_SLUG from the architecture output.\n\n"
            "## Required files — write ALL using FileWriterTool:\n"
            "- projects/<slug>/README.md — MUST include:\n"
            "    • Project overview (1–2 paragraphs)\n"
            "    • Architecture diagram (ASCII or Mermaid)\n"
            "    • Prerequisites (Docker 24+, Node 20+, Python 3.12+)\n"
            "    • Quickstart: `cp .env.example .env && docker compose up` "
            "(must work in 2 commands)\n"
            "    • Development setup: backend venv + uvicorn --reload, "
            "frontend npm install + next dev\n"
            "    • Environment variables table (name | default | description)\n"
            "    • API reference: each endpoint with method, path, "
            "request body, response, and curl example\n"
            "    • Testing: how to run pytest and vitest\n"
            "    • Contributing guidelines\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "README.md written to projects/<slug>/. "
            "Final Answer: one-paragraph summary of what was documented."
        ),
        agent=tech_writer,
        output_file="output/05_docs.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Final Approval (Team Leader quality gate)
# ─────────────────────────────────────────────────────────────────────────────

def create_approval_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Review ALL deliverables produced for:\n\n{feature_description}\n\n"
            "All previous task outputs are in your context: architecture, backend, "
            "frontend, tests, devops, and documentation.\n\n"
            "## Review checklist\n"
            "1. **Architecture compliance** — Does the implemented code match the "
            "API contract, data models, and folder structure in ARCHITECTURE.md?\n"
            "2. **Completeness** — Are all required files listed in the architecture "
            "actually present in the outputs?\n"
            "3. **Type alignment** — Do the TypeScript/Zod schemas in the frontend "
            "match the Pydantic models in the backend field-by-field?\n"
            "4. **Test coverage** — Does the test suite cover all API endpoints "
            "(happy path + error cases + at least one edge case each)?\n"
            "5. **DevOps readiness** — Are Dockerfiles, docker-compose, and CI workflow "
            "complete and consistent with the actual project structure?\n"
            "6. **Documentation accuracy** — Does the README reflect the actual "
            "commands, endpoints, and environment variables?\n"
            "7. **Security** — Are there any OWASP Top 10 issues in the backend code "
            "or configuration files (hardcoded secrets, missing validation, etc.)?\n\n"
            "## Output format\n"
            "Your Final Answer MUST begin with exactly one of:\n"
            "  VERDICT: APPROVED\n"
            "  VERDICT: REJECTED\n\n"
            "If REJECTED, list every issue in this format:\n"
            "  [SEVERITY: Critical|Major|Minor] | <area> | <issue> | <required fix>\n\n"
            "If APPROVED, provide a concise summary of what was reviewed and confirmed."
        ),
        expected_output=(
            "First line: `VERDICT: APPROVED` or `VERDICT: REJECTED`\n"
            "If REJECTED: numbered, prioritised list of all issues with severity, "
            "area, description, and required fix.\n"
            "If APPROVED: a short paragraph confirming what was verified."
        ),
        agent=team_leader,
        output_file="output/06_approval.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 8. Code Review  (Phase 2 quality gate — used by orchestrator)
# ─────────────────────────────────────────────────────────────────────────────

def create_code_review_task(sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} — Code Review\n\n"
            "Review the backend and frontend implementation outputs in your context.\n\n"
            "## Review scope\n"
            "1. **Architecture compliance** — Does the code match the API contract "
            "in ARCHITECTURE.md exactly?\n"
            "2. **Code quality** — DRY/SOLID principles, naming conventions, no dead code\n"
            "3. **Security (OWASP Top 10)** — Input validation, parameterised SQL, "
            "no hardcoded secrets, CORS configured correctly\n"
            "4. **Error handling** — All edge cases and 4xx/5xx paths handled?\n"
            "5. **Type alignment** — Do TypeScript/Zod types mirror Pydantic models "
            "field-by-field?\n\n"
            "## Output format\n"
            "List every finding using this format:\n"
            "[SEVERITY: Critical|Major|Minor] | <file> | <issue> | <required fix>\n\n"
            "End your response with one of:\n"
            "REVIEW SUMMARY: CLEAN  (no Critical or Major issues)\n"
            "REVIEW SUMMARY: ISSUES FOUND  (any Critical or Major issues exist)"
        ),
        expected_output=(
            "Structured finding list in [SEVERITY] | file | issue | fix format.\n"
            "Final line: REVIEW SUMMARY: CLEAN or REVIEW SUMMARY: ISSUES FOUND."
        ),
        agent=code_reviewer,
        output_file=f"output/review_sprint_{sprint}.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 9. Development Gate  (Team Leader evaluates impl + code review)
# ─────────────────────────────────────────────────────────────────────────────

def create_dev_gate_task(feature_description: str, sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} Development Gate — Quality Evaluation\n\n"
            f"Feature: {feature_description}\n\n"
            "Architecture, implementation, and code review are in your context. "
            "Decide whether the implementation is ready to move to testing.\n\n"
            "## APPROVE if:\n"
            "- Code review is REVIEW SUMMARY: CLEAN, or only Minor issues remain\n"
            "- All required files from ARCHITECTURE.md are present\n"
            "- Full API contract is implemented\n\n"
            "## REJECT if:\n"
            "- Any Critical security or correctness issue exists\n"
            "- More than 2 Major issues exist\n"
            "- Required files are missing\n\n"
            "## MANDATORY — your Final Answer MUST begin with:\n"
            "VERDICT: APPROVED  or  VERDICT: REJECTED\n\n"
            f"If REJECTED, list exactly what must be fixed before Sprint {sprint + 1}."
        ),
        expected_output=(
            "First line: `VERDICT: APPROVED` or `VERDICT: REJECTED`.\n"
            "If REJECTED: numbered list of required fixes with file references."
        ),
        agent=team_leader,
        output_file=f"output/dev_gate_sprint_{sprint}.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 10. Backend Revision  (triggered by REJECTED dev gate)
# ─────────────────────────────────────────────────────────────────────────────

def create_backend_revision_task(feature_description: str, feedback: str) -> Task:
    return Task(
        description=(
            "Backend Revision — address all findings from the previous sprint.\n\n"
            f"Feature: {feature_description}\n\n"
            "## Issues to fix (from Team Leader / Code Review):\n"
            f"{feedback}\n\n"
            "## Instructions\n"
            "- Address EVERY issue listed above\n"
            "- For each fix: state which issue it resolves, then write the corrected file\n"
            "- Use FileWriterTool to rewrite every modified file\n"
            "- Do NOT change files unrelated to the listed issues\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "For each issue: the fix applied and the file updated. "
            "All corrected files written to disk under projects/<slug>/backend/."
        ),
        agent=backend_developer,
        output_file="output/backend_revision.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 11. Frontend Revision  (triggered by REJECTED dev gate or test gate)
# ─────────────────────────────────────────────────────────────────────────────

def create_frontend_revision_task(feature_description: str, feedback: str) -> Task:
    return Task(
        description=(
            "Frontend Revision — address all findings from the previous sprint.\n\n"
            f"Feature: {feature_description}\n\n"
            "## Issues to fix (from Team Leader / Code Review / Tests):\n"
            f"{feedback}\n\n"
            "## Instructions\n"
            "- Address EVERY issue listed above\n"
            "- For each fix: state which issue it resolves, then write the corrected file\n"
            "- Use FileWriterTool to rewrite every modified file\n"
            "- After fixes ensure Zod schemas still mirror Pydantic models exactly\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "For each issue: the fix applied and the file updated. "
            "All corrected files written to disk under projects/<slug>/frontend/."
        ),
        agent=frontend_developer,
        output_file="output/frontend_revision.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 12. Test Gate  (Team Leader evaluates test results)
# ─────────────────────────────────────────────────────────────────────────────

def create_test_gate_task(feature_description: str, sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} Test Gate — Quality Evaluation\n\n"
            f"Feature: {feature_description}\n\n"
            "Architecture, implementation, and test results are in your context. "
            "Decide whether the test results are acceptable to proceed to DevOps.\n\n"
            "## APPROVE if:\n"
            "- All tests pass, or only Minor/cosmetic failures remain\n"
            "- Every API endpoint has test coverage\n"
            "- No security-related test failures\n\n"
            "## REJECT if:\n"
            "- Any Critical test failure (broken endpoint, data corruption, auth bypass)\n"
            "- More than 2 Major failures\n"
            "- Core endpoint tests are missing\n\n"
            "## MANDATORY — your Final Answer MUST begin with:\n"
            "VERDICT: APPROVED  or  VERDICT: REJECTED\n\n"
            f"If REJECTED, list exactly what must be fixed before re-testing in Sprint {sprint + 1}."
        ),
        expected_output=(
            "First line: `VERDICT: APPROVED` or `VERDICT: REJECTED`.\n"
            "If REJECTED: numbered list of required fixes with test file references."
        ),
        agent=team_leader,
        output_file=f"output/test_gate_sprint_{sprint}.md",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 13. Retest  (after code fixes triggered by REJECTED test gate)
# ─────────────────────────────────────────────────────────────────────────────

def create_retest_task(feedback: str) -> Task:
    return Task(
        description=(
            "Re-run the full test suite after the development team applied the "
            "fixes requested in the previous Test Gate.\n\n"
            "## Issues that were fixed and MUST now pass:\n"
            f"{feedback}\n\n"
            "## Instructions\n"
            "1. Use FileReadTool to read the latest implementation files\n"
            "2. Re-run ALL tests — including those that previously failed\n"
            "3. For each previously failing test, explicitly report PASS or FAIL\n"
            "4. Write updated test files if any corrections to the test code are needed\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "Full test results per test case (PASS/FAIL). "
            "Explicit confirmation that each previously failing test now passes, "
            "or a clear explanation if it still fails."
        ),
        agent=test_engineer,
        output_file="output/retest.md",
    )

