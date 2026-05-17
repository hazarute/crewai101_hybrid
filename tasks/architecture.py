"""tasks/architecture.py — Architecture task: Project Architect designs and scaffolds the project."""

from crewai import Task

from agents.project_architect import project_architect


_FILE_EMBED_FORMAT = (
    "Embed each file in your Final Answer using this EXACT format "
    "(the orchestrator extracts and writes them automatically):\n\n"
    "=== FILE: projects/<slug>/relative/path/to/file ===\n"
    "```lang\n"
    "<content>\n"
    "```\n"
    "=== END FILE ==="
)


def create_architecture_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Design the complete project for:\n\n{feature_description}\n\n"
            "Determine the target platform (web / mobile / universal), choose a project slug, "
            "and produce the full architecture: API contract, data models, folder structure, "
            "and technology choices.\n\n"
            "## Output — embed these 5 scaffolding files using the format below:\n"
            "  1. projects/<slug>/ARCHITECTURE.md — full design document\n"
            "     (line 1: `PROJECT_SLUG: <slug>`, line 2: `PLATFORM: web|mobile|universal`)\n"
            "  2. projects/<slug>/backend/pyproject.toml\n"
            "  3. projects/<slug>/frontend/package.json  (web)  OR\n"
            "     projects/<slug>/mobile/package.json  (mobile/universal)\n"
            "  4. projects/<slug>/.gitignore\n"
            "  5. projects/<slug>/.env.example\n\n"
            f"{_FILE_EMBED_FORMAT}\n\n"
            "## MANDATORY — your Final Answer MUST begin with:\n"
            "PROJECT_SLUG: <slug>\n"
            "PLATFORM: web | mobile | universal"
        ),
        expected_output=(
            "First two lines: `PROJECT_SLUG: <slug>` and `PLATFORM: web|mobile|universal`.\n"
            "Five scaffolding files in === FILE: === format. "
            "ARCHITECTURE.md contains API contract, data models, folder tree, and tech choices."
        ),
        agent=project_architect,
        output_file="output/00_architecture.md",
    )
