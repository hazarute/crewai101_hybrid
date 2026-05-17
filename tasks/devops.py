"""tasks/devops.py — DevOps task: Docker, CI/CD, EAS Build configuration."""

from crewai import Task

from agents.devops_agent import devops_agent
from tasks._shared import _FILE_FORMAT_HELP, _FILE_WRITER_RULE


def create_devops_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Set up the DevOps configuration for:\n\n{feature_description}\n\n"
            "The full implementation and architecture are in your context. "
            "Read ARCHITECTURE.md for PLATFORM and folder structure, then produce the "
            "appropriate Docker, CI/CD, and (for mobile/universal) EAS Build files.\n\n"
            f"{_FILE_WRITER_RULE}\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All DevOps files written to disk. "
            "Final Answer: file list and a brief deployment architecture summary."
        ),
        agent=devops_agent,
        output_file="output/04_devops.md",
    )
