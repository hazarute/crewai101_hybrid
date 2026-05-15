"""
tasks/task_definitions.py — Task factory functions for the Hybrid AI Agency.

Pipeline:
  Project Architect → Python Backend → TypeScript Frontend / Mobile →
  QA Engineer → DevOps Engineer → Technical Writer

Platform support:
  web       → Next.js 14 App Router + TypeScript + Tailwind CSS + Zod
  mobile    → React Native + Expo SDK 52 + Tamagui + TypeScript + Zod
  universal → React Native (Expo) + Tamagui (iOS + Android + Web)

The Project Architect detects the platform from the feature request and
declares it in ARCHITECTURE.md as:  PLATFORM: web | mobile | universal
All downstream tasks read and respect that declaration.

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
            "## Step 1 — Detect the target platform\n"
            "Read the feature request carefully and choose ONE platform:\n"
            "  • **web** — website, dashboard, web portal, browser app (default)\n"
            "  • **mobile** — iOS app, Android app, mobile app, native app\n"
            "  • **universal** — cross-platform, both web and mobile, universal app\n\n"
            "## Step 2 — Choose a project slug\n"
            "Concise, lowercase, kebab-case (e.g. reverse-api, todo-app, fitness-tracker).\n\n"
            "## Step 3 — Confirm the full tech stack based on platform:\n"
            "  **web** stack:\n"
            "    - Backend: FastAPI + Pydantic v2 + SQLModel + Alembic + Python 3.12\n"
            "    - Frontend: Next.js 14 App Router + TypeScript 5 + Tailwind CSS + Zod\n"
            "  **mobile** stack:\n"
            "    - Backend: FastAPI + Pydantic v2 + SQLModel + Alembic + Python 3.12\n"
            "    - Mobile: React Native + Expo SDK 52 + Tamagui + TypeScript 5 + Zod\n"
            "      (Expo Router v3 for navigation, TanStack Query v5 for data fetching)\n"
            "  **universal** stack:\n"
            "    - Backend: FastAPI + Pydantic v2 + SQLModel + Alembic + Python 3.12\n"
            "    - App: React Native (Expo SDK 52) + Tamagui + TypeScript 5 + Zod\n"
            "      (Expo Router v3 with web support, runs on iOS, Android, and Web)\n\n"
            "## Step 4 — Define every API endpoint\n"
            "HTTP method, path, request body schema, response schema, HTTP status codes.\n\n"
            "## Step 5 — Define every data model\n"
            "Pydantic schema + SQLModel table.\n\n"
            "## Step 6 — Define the complete folder structure\n"
            "  web:       projects/<slug>/backend/  +  projects/<slug>/frontend/\n"
            "  mobile:    projects/<slug>/backend/  +  projects/<slug>/mobile/\n"
            "  universal: projects/<slug>/backend/  +  projects/<slug>/mobile/\n\n"
            "## Step 7 — Write these files using FileWriterTool:\n"
            "  a) projects/<slug>/ARCHITECTURE.md — full design doc:\n"
            "     MUST include on line 2: `PLATFORM: web` or `PLATFORM: mobile` or "
            "`PLATFORM: universal`\n"
            "     Then: API contract, models, folder tree, tech rationale\n"
            "  b) projects/<slug>/backend/pyproject.toml\n"
            "  c) For web: projects/<slug>/frontend/package.json\n"
            "     For mobile/universal: projects/<slug>/mobile/package.json\n"
            "       (must include: expo, react-native, @tamagui/core, tamagui, "
            "@tamagui/config, expo-router, @tanstack/react-query, zod)\n"
            "  d) projects/<slug>/.gitignore (include .expo/ and node_modules/)\n"
            "  e) projects/<slug>/.env.example\n\n"
            f"{_FILE_FORMAT_HELP}\n\n"
            "## MANDATORY — your Final Answer MUST begin with exactly:\n"
            "PROJECT_SLUG: <the-slug-you-chose>\n"
            "PLATFORM: web | mobile | universal\n"
            "followed by a summary of all files written and the complete API contract."
        ),
        expected_output=(
            "First two lines:\n"
            "  `PROJECT_SLUG: <slug>`\n"
            "  `PLATFORM: web | mobile | universal`\n"
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
            "Extract PROJECT_SLUG and PLATFORM from the architecture output "
            "(first two lines: `PROJECT_SLUG: <slug>` and `PLATFORM: web|mobile|universal`).\n\n"
            "═══════════════════════════════════════════════════════════\n"
            "IF PLATFORM == web\n"
            "═══════════════════════════════════════════════════════════\n"
            "Target dir: projects/<slug>/frontend/\n\n"
            "## Required files — write ALL using FileWriterTool:\n"
            "- src/app/layout.tsx\n"
            "- src/app/page.tsx\n"
            "- src/app/globals.css\n"
            "- src/components/<FeatureName>.tsx  (main feature component)\n"
            "- src/lib/api.ts       (typed API client, all fetch calls)\n"
            "- src/lib/types.ts     (Zod schemas mirroring backend Pydantic models)\n"
            "- next.config.mjs      (/api/* proxied to http://localhost:8000)\n"
            "- tailwind.config.ts   (include CSS variable color mappings)\n"
            "- tsconfig.json        (strict mode enabled)\n"
            "- package.json         (if not already written)\n\n"
            "## Web implementation requirements:\n"
            "- Next.js 14 App Router + TypeScript strict mode\n"
            "- Tailwind CSS with full CSS variable color palette in tailwind.config.ts\n"
            "- Zod schemas that mirror the backend Pydantic models exactly\n"
            "- Handle loading, error, and empty states in every UI component\n"
            "- Accessible: semantic HTML, aria labels where helpful\n"
            "- Use next.config.mjs (NOT next.config.ts) for Next.js 14 compatibility\n\n"
            "═══════════════════════════════════════════════════════════\n"
            "IF PLATFORM == mobile OR PLATFORM == universal\n"
            "═══════════════════════════════════════════════════════════\n"
            "Target dir: projects/<slug>/mobile/\n\n"
            "## Required files — write ALL using FileWriterTool:\n"
            "- app.json              (Expo config: name, slug, version, platforms,\n"
            "                         bundleIdentifier, icon, splash, permissions)\n"
            "- tamagui.config.ts     (Tamagui theme: defaultConfig, tokens, themes,\n"
            "                         shorthands — import from @tamagui/config/v4)\n"
            "- babel.config.js       (expo preset + tamagui/babel plugin)\n"
            "- metro.config.js       (withTamagui metro wrapper)\n"
            "- tsconfig.json         (strict mode, extends expo/tsconfig.base)\n"
            "- package.json          (if not already written; must include:\n"
            "                         expo, react-native, @tamagui/core, tamagui,\n"
            "                         @tamagui/config, expo-router, @tanstack/react-query,\n"
            "                         zod, react-native-mmkv, expo-status-bar)\n"
            "- app/_layout.tsx       (root layout: TamaguiProvider wrapping Stack/Tabs)\n"
            "- app/(tabs)/_layout.tsx (tab bar: Tabs from expo-router)\n"
            "- app/(tabs)/index.tsx  (main home screen)\n"
            "- components/<FeatureName>.tsx (main feature component using Tamagui)\n"
            "- lib/api.ts            (typed API client using fetch; base URL from env)\n"
            "- lib/types.ts          (Zod schemas mirroring backend Pydantic models)\n"
            "- constants/Colors.ts   (light/dark theme color tokens)\n\n"
            "## Mobile/Universal implementation requirements:\n"
            "- React Native + Expo SDK 52 managed workflow\n"
            "- Tamagui components ONLY for UI — do NOT use StyleSheet or Tailwind\n"
            "  Use: Stack, XStack, YStack, Text, Button, Input, ScrollView, Card,\n"
            "       Separator, Image, Sheet, Dialog, Toast, Spinner from tamagui\n"
            "- Wrap root with: <TamaguiProvider config={tamaguiConfig}> and\n"
            "  <QueryClientProvider client={queryClient}>\n"
            "- Handle loading (Spinner), error (Text color='$red10'), and empty states\n"
            "- Zod schemas that mirror backend Pydantic models exactly\n"
            "- API base URL from process.env.EXPO_PUBLIC_API_URL\n"
            "  (defaults to http://localhost:8000)\n"
            "- Accessible: accessibilityLabel on all interactive elements\n"
            "- For universal: add 'web' to platforms in app.json; Expo Router handles routing\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All frontend/mobile source files written to projects/<slug>/frontend/ "
            "(web) or projects/<slug>/mobile/ (mobile/universal). "
            "Final Answer lists every file created and confirms the PLATFORM used."
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
            "TypeScript frontend (web or mobile).\n"
            "The full implementation is in your context. "
            "Extract PROJECT_SLUG and PLATFORM from the architecture output.\n\n"
            "## Backend tests (pytest) — write to projects/<slug>/backend/tests/:\n"
            "- tests/__init__.py\n"
            "- tests/conftest.py  "
            "(pytest fixtures: async test client, in-memory SQLite DB)\n"
            "- tests/test_api.py  "
            "(≥ 3 test cases per endpoint: 200 happy path, 422 validation, edge case)\n\n"
            "═══════════════════════════════════════════════════════════\n"
            "IF PLATFORM == web  →  write to projects/<slug>/frontend/__tests__/\n"
            "═══════════════════════════════════════════════════════════\n"
            "- __tests__/setup.ts           (Vitest + Testing Library + happy-dom config)\n"
            "- __tests__/<Component>.test.tsx  "
            "(render, user interaction, API mock via MSW)\n"
            "- Use: Vitest, @testing-library/react, @testing-library/user-event, MSW\n\n"
            "═══════════════════════════════════════════════════════════\n"
            "IF PLATFORM == mobile | universal  →  write to projects/<slug>/mobile/__tests__/\n"
            "═══════════════════════════════════════════════════════════\n"
            "- __tests__/setup.ts           (jest-expo preset config, Tamagui provider mock,\n"
            "                                MSW server setup for API mocking)\n"
            "- __tests__/<Component>.test.tsx  (render with TamaguiProvider + QueryClientProvider,\n"
            "                                   fireEvent for user interactions, MSW for API)\n"
            "- Use: Jest, jest-expo, @testing-library/react-native, MSW\n"
            "- jest.config.js: preset='jest-expo', transform={tsx: babel-jest}\n"
            "- Mock expo-router with jest.mock('expo-router')\n"
            "- Test all component states: loading (Spinner visible), "
            "success (data rendered), error (error Text visible)\n\n"
            "## Common requirements\n"
            "- Use httpx.AsyncClient for backend endpoint tests\n"
            "- Test all component states: initial render, loading, success, error\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All test files written to disk. "
            "Final Answer: list of test files + summary of coverage scope "
            "and which framework was used (Vitest or Jest)."
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
            "Extract PROJECT_SLUG and PLATFORM from the architecture output.\n\n"
            "═══════════════════════════════════════════════════════════\n"
            "FOR ALL PLATFORMS — Backend service files:\n"
            "═══════════════════════════════════════════════════════════\n"
            "- projects/<slug>/backend/Dockerfile          "
            "(multi-stage: builder + runtime, non-root user, HEALTHCHECK)\n"
            "- projects/<slug>/.env.example                "
            "(all required env vars with descriptions)\n\n"
            "═══════════════════════════════════════════════════════════\n"
            "IF PLATFORM == web  →  web-specific DevOps files:\n"
            "═══════════════════════════════════════════════════════════\n"
            "- projects/<slug>/frontend/Dockerfile         "
            "(multi-stage: node builder + nginx runtime)\n"
            "- projects/<slug>/docker-compose.yml          "
            "(backend + frontend + optional db with health checks)\n"
            "- projects/<slug>/.github/workflows/ci.yml    "
            "(lint → test → build → push Docker images; deploy only on main)\n"
            "- projects/<slug>/smoke_test.sh               "
            "(curl checks for all critical endpoints)\n\n"
            "═══════════════════════════════════════════════════════════\n"
            "IF PLATFORM == mobile | universal  →  mobile-specific DevOps files:\n"
            "═══════════════════════════════════════════════════════════\n"
            "- projects/<slug>/mobile/eas.json             "
            "(EAS Build profiles: development, preview, production;\n"
            " platforms: android + ios; distribution: store for production)\n"
            "- projects/<slug>/.github/workflows/ci.yml    "
            "(jobs: backend-test → mobile-build;\n"
            " backend-test: pytest; mobile-build: npm install + eas build --non-interactive;\n"
            " eas submit on main branch with EXPO_TOKEN secret)\n"
            "- projects/<slug>/smoke_test.sh               "
            "(curl checks for all backend API endpoints)\n\n"
            "IF PLATFORM == universal, ALSO add web DevOps files above.\n\n"
            "## Common requirements\n"
            "- Docker multi-stage builds with layer caching optimisation\n"
            "- Non-root user in every Docker container\n"
            "- CI runs tests before building Docker images or EAS builds\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All DevOps files written to disk. "
            "Final Answer: file list + deployment architecture summary "
            "explaining web (Docker) and/or mobile (EAS) deployment strategy."
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
            "Extract PROJECT_SLUG and PLATFORM from the architecture output.\n\n"
            "## Required files — write ALL using FileWriterTool:\n"
            "- projects/<slug>/README.md — MUST include:\n"
            "    • Project overview (1–2 paragraphs)\n"
            "    • Architecture diagram (ASCII or Mermaid)\n"
            "    • PLATFORM badge (Web App | Mobile App | Universal App)\n\n"
            "══ IF PLATFORM == web ══\n"
            "    • Prerequisites: Docker 24+, Node 20+, Python 3.12+\n"
            "    • Quickstart: `cp .env.example .env && docker compose up`\n"
            "    • Development setup: backend venv + uvicorn --reload, "
            "frontend npm install + next dev\n"
            "    • Environment variables table\n"
            "    • API reference: each endpoint with method, path, "
            "request body, response, curl example\n"
            "    • Testing: `pytest` (backend) + `vitest run` (frontend)\n\n"
            "══ IF PLATFORM == mobile ══\n"
            "    • Prerequisites: Node 20+, Python 3.12+, Expo CLI (`npm i -g expo-cli`),\n"
            "      EAS CLI (`npm i -g eas-cli`), Expo Go app on device/simulator\n"
            "    • Backend quickstart: `cd backend && uvicorn app.main:app --reload`\n"
            "    • Mobile quickstart: `cd mobile && npx expo start`\n"
            "    • Expo Go: scan QR code with Expo Go app to run on device\n"
            "    • EAS Build: `eas build --platform all` (builds iOS + Android)\n"
            "    • EAS Submit: `eas submit --platform all` (App Store + Google Play)\n"
            "    • OTA Updates: `eas update --branch production`\n"
            "    • Environment variables: EXPO_PUBLIC_API_URL, EAS_TOKEN\n"
            "    • API reference with curl examples\n"
            "    • Testing: `pytest` (backend) + `jest` (mobile)\n\n"
            "══ IF PLATFORM == universal ══\n"
            "    Include BOTH web and mobile sections above.\n"
            "    Add: Running on Web: `npx expo start --web`\n"
            "    Add: Running on Mobile: Expo Go instructions\n\n"
            "    • Contributing guidelines (all platforms)\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "README.md written to projects/<slug>/. "
            "Final Answer: one-paragraph summary of what was documented and "
            "which platform sections were included."
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
            "frontend/mobile, tests, devops, and documentation.\n\n"
            "## Review checklist\n"
            "1. **Architecture compliance** — Does the implemented code match the "
            "API contract, data models, and folder structure in ARCHITECTURE.md?\n"
            "2. **Platform compliance** — Is PLATFORM (web/mobile/universal) respected?\n"
            "   - web: Next.js + Tailwind CSS files present\n"
            "   - mobile/universal: React Native + Expo + Tamagui files present "
            "(app.json, tamagui.config.ts, app/_layout.tsx, Expo Router structure)\n"
            "3. **Completeness** — Are all required files listed in the architecture "
            "actually present in the outputs?\n"
            "4. **Type alignment** — Do TypeScript/Zod schemas in the frontend/mobile "
            "match the Pydantic models in the backend field-by-field?\n"
            "5. **Test coverage** — Does the test suite cover all API endpoints "
            "(happy path + error cases + at least one edge case each)?\n"
            "   - web: Vitest tests present\n"
            "   - mobile/universal: Jest + @testing-library/react-native tests present\n"
            "6. **DevOps readiness** — Are required CI/CD files complete?\n"
            "   - web: Dockerfiles + docker-compose + GitHub Actions\n"
            "   - mobile/universal: eas.json + GitHub Actions with EAS Build\n"
            "7. **Documentation accuracy** — Does the README reflect the actual "
            "commands, endpoints, environment variables, and platform-specific setup?\n"
            "8. **Security** — Are there any OWASP Top 10 issues in the backend code "
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
            "Review the backend and frontend/mobile implementation outputs in your context.\n\n"
            "## Review scope\n"
            "1. **Architecture compliance** — Does the code match the API contract "
            "in ARCHITECTURE.md exactly?\n"
            "2. **Platform compliance** — Check PLATFORM in ARCHITECTURE.md:\n"
            "   - web: Next.js App Router structure, Tailwind classes, next.config.mjs proxy\n"
            "   - mobile/universal: Expo managed workflow, Tamagui components only (no StyleSheet),\n"
            "     app.json with bundleIdentifier, tamagui.config.ts with theme tokens,\n"
            "     TamaguiProvider wrapping root layout, Expo Router file structure\n"
            "3. **Code quality** — DRY/SOLID principles, naming conventions, no dead code\n"
            "4. **Security (OWASP Top 10)** — Input validation, parameterised SQL, "
            "no hardcoded secrets, CORS configured correctly, no sensitive data in "
            "EXPO_PUBLIC_ env vars (those are public)\n"
            "5. **Error handling** — All edge cases and 4xx/5xx paths handled?\n"
            "6. **Type alignment** — Do TypeScript/Zod types mirror Pydantic models "
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
            "Frontend/Mobile Revision — address all findings from the previous sprint.\n\n"
            f"Feature: {feature_description}\n\n"
            "## Issues to fix (from Team Leader / Code Review / Tests):\n"
            f"{feedback}\n\n"
            "## Instructions\n"
            "- Address EVERY issue listed above\n"
            "- Read PLATFORM from ARCHITECTURE.md before writing files\n"
            "- For each fix: state which issue it resolves, then write the corrected file\n"
            "- Use FileWriterTool to rewrite every modified file\n"
            "- web: ensure Zod schemas still mirror Pydantic models exactly\n"
            "- mobile/universal: ensure Tamagui components are used (no StyleSheet),\n"
            "  TamaguiProvider wraps root layout, and Zod schemas mirror Pydantic models\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "For each issue: the fix applied and the file updated. "
            "All corrected files written to disk under projects/<slug>/frontend/ "
            "(web) or projects/<slug>/mobile/ (mobile/universal)."
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

