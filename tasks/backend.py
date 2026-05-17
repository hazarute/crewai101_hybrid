"""tasks/backend.py — Backend tasks: implementation + revision."""

from crewai import Task

from agents.backend_developer import backend_developer
from tasks._shared import _FILE_FORMAT_HELP, _FILE_WRITER_RULE


def create_backend_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Implement the Python backend for:\n\n{feature_description}\n\n"
            "The architecture document is in your context. "
            "Read ARCHITECTURE.md to find the folder structure, API contract, and data models. "
            "Implement every backend file listed in the folder tree.\n\n"
            f"{_FILE_WRITER_RULE}\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All backend files written to projects/<slug>/backend/. "
            "Final Answer lists every file created and the API endpoints implemented."
        ),
        agent=backend_developer,
        output_file="output/01_backend.md",
    )


def create_backend_revision_task(feature_description: str, feedback: str) -> Task:
    return Task(
        description=(
            f"Fix the following backend issues:\n\n{feedback}\n\n"
            f"{_FILE_WRITER_RULE}\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "Each issue addressed and its file rewritten. "
            "Final Answer lists every corrected file under projects/<slug>/backend/."
        ),
        agent=backend_developer,
        output_file="output/backend_revision.md",
    )
