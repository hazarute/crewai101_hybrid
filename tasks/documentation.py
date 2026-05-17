"""tasks/documentation.py — Documentation task: README and project docs."""

from crewai import Task

from agents.tech_writer import tech_writer
from tasks._shared import _FILE_FORMAT_HELP, _FILE_WRITER_RULE


def create_documentation_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Write the project README for:\n\n{feature_description}\n\n"
            "The full implementation and architecture are in your context. "
            "Read ARCHITECTURE.md for the API contract, PLATFORM, and folder structure. "
            "Cover setup instructions, environment variables, API reference, and "
            "testing/deployment commands appropriate for the detected platform.\n\n"
            f"{_FILE_WRITER_RULE}\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "README.md written to projects/<slug>/. "
            "Final Answer: summary of sections included and which platform was covered."
        ),
        agent=tech_writer,
        output_file="output/05_docs.md",
    )
