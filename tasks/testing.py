"""tasks/testing.py — Testing tasks: test suite authoring + retest after fixes."""

from crewai import Task

from agents.test_engineer import test_engineer
from tasks._shared import _FILE_FORMAT_HELP, _FILE_WRITER_RULE


def create_testing_task() -> Task:
    return Task(
        description=(
            "Write test suites for the project.\n\n"
            "The full implementation and architecture are in your context. "
            "Read ARCHITECTURE.md for the API contract (all endpoints to test) and "
            "PLATFORM to choose the correct testing framework. "
            "Write backend tests (pytest) and frontend tests (Vitest for web, "
            "Jest for mobile/universal).\n\n"
            f"{_FILE_WRITER_RULE}\n\n"
            f"{_FILE_FORMAT_HELP}"
        ),
        expected_output=(
            "All test files written to disk. "
            "Final Answer: list of test files and a summary of coverage scope."
        ),
        agent=test_engineer,
        output_file="output/03_tests.md",
    )


def create_retest_task(feedback: str) -> Task:
    return Task(
        description=(
            f"Re-run and fix the tests for the following previously failing issues:\n\n{feedback}"
        ),
        expected_output=(
            "Explicit PASS or FAIL result per previously failing test. "
            "Updated test files written if corrections were needed."
        ),
        agent=test_engineer,
        output_file="output/retest.md",
    )
