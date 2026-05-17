"""tasks/frontend.py — Frontend tasks: implementation + revision (web, mobile, universal)."""

from crewai import Task

from agents.frontend_developer import frontend_developer
from tasks._shared import _FILE_FORMAT_HELP, _FILE_WRITER_RULE


def create_frontend_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Implement the frontend for:\n\n{feature_description}\n\n"
            "The architecture document and backend implementation are in your context. "
            "Read ARCHITECTURE.md to find PLATFORM, the folder structure, and the API contract. "
            "Implement every frontend file listed in the folder tree.\n\n"
            f"{_FILE_WRITER_RULE}\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All frontend files written to projects/<slug>/frontend/ (web) or "
            "projects/<slug>/mobile/ (mobile/universal). "
            "Final Answer lists every file created and confirms the PLATFORM used."
        ),
        agent=frontend_developer,
        output_file="output/02_frontend.md",
    )


def create_frontend_revision_task(feature_description: str, feedback: str) -> Task:
    return Task(
        description=(
            f"Fix the following frontend issues:\n\n{feedback}\n\n"
            f"{_FILE_WRITER_RULE}\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "Each issue addressed and its file rewritten. "
            "Final Answer lists every corrected file under projects/<slug>/frontend/ "
            "or projects/<slug>/mobile/."
        ),
        agent=frontend_developer,
        output_file="output/frontend_revision.md",
    )
