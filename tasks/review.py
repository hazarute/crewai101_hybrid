"""tasks/review.py — Code review tasks: full, backend-only, and frontend-only reviews."""

from crewai import Task

from agents.code_reviewer import code_reviewer


def create_code_review_task(sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} — Review the backend and frontend implementation.\n\n"
            "Compare the produced code against ARCHITECTURE.md (API contract, data models, "
            "folder structure, platform requirements). Report each finding as:\n"
            "[SEVERITY: Critical|Major|Minor] | <file> | <issue> | <required fix>\n\n"
            "End with:\n"
            "REVIEW SUMMARY: CLEAN  (no Critical or Major issues)\n"
            "REVIEW SUMMARY: ISSUES FOUND  (any Critical or Major issues present)"
        ),
        expected_output=(
            "Findings in [SEVERITY] | file | issue | fix format. "
            "Final line: REVIEW SUMMARY: CLEAN or REVIEW SUMMARY: ISSUES FOUND."
        ),
        agent=code_reviewer,
        output_file=f"output/review_sprint_{sprint}.md",
    )


def create_backend_review_task(sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} — Review the backend implementation.\n\n"
            "Compare the produced code against ARCHITECTURE.md (API contract, data models, "
            "folder structure). Report each finding as:\n"
            "[SEVERITY: Critical|Major|Minor] | <file> | <issue> | <required fix>\n\n"
            "End with:\n"
            "REVIEW SUMMARY: CLEAN  (no Critical or Major issues)\n"
            "REVIEW SUMMARY: ISSUES FOUND  (any Critical or Major issues present)"
        ),
        expected_output=(
            "Findings in [SEVERITY] | file | issue | fix format. "
            "Final line: REVIEW SUMMARY: CLEAN or REVIEW SUMMARY: ISSUES FOUND."
        ),
        agent=code_reviewer,
        output_file=f"output/backend_review_sprint_{sprint}.md",
    )


def create_frontend_review_task(sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} — Review the frontend implementation.\n\n"
            "Compare the produced code against ARCHITECTURE.md (API contract, platform "
            "requirements, folder structure, type alignment with backend models). "
            "Report each finding as:\n"
            "[SEVERITY: Critical|Major|Minor] | <file> | <issue> | <required fix>\n\n"
            "End with:\n"
            "REVIEW SUMMARY: CLEAN  (no Critical or Major issues)\n"
            "REVIEW SUMMARY: ISSUES FOUND  (any Critical or Major issues present)"
        ),
        expected_output=(
            "Findings in [SEVERITY] | file | issue | fix format. "
            "Final line: REVIEW SUMMARY: CLEAN or REVIEW SUMMARY: ISSUES FOUND."
        ),
        agent=code_reviewer,
        output_file=f"output/frontend_review_sprint_{sprint}.md",
    )
