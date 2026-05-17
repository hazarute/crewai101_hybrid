"""tasks/gates.py — Quality gate tasks: backend gate, frontend gate, test gate, final approval."""

from crewai import Task

from agents.team_leader import team_leader


def create_dev_gate_task(feature_description: str, sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} — Decide if the full implementation is ready for testing.\n\n"
            "The architecture, implementation, and code review are in your context. "
            "The review already inspected the actual files on disk — trust its findings.\n\n"
            "APPROVE if the review shows no Critical issues and at most 2 Major issues. "
            "REJECT otherwise.\n\n"
            "Your Final Answer MUST begin with:\n"
            "VERDICT: APPROVED  or  VERDICT: REJECTED\n\n"
            f"If REJECTED, list what must be fixed before Sprint {sprint + 1}."
        ),
        expected_output=(
            "First line: `VERDICT: APPROVED` or `VERDICT: REJECTED`. "
            "If REJECTED: list of required fixes."
        ),
        agent=team_leader,
        output_file=f"output/dev_gate_sprint_{sprint}.md",
    )


def create_backend_gate_task(feature_description: str, sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} — Decide if the backend is ready to proceed to frontend development.\n\n"
            "The architecture and backend code review are in your context. "
            "The review already inspected the actual files on disk — trust its findings.\n\n"
            "APPROVE if the review shows no Critical issues and at most 2 Major issues. "
            "REJECT otherwise.\n\n"
            "Your Final Answer MUST begin with:\n"
            "VERDICT: APPROVED  or  VERDICT: REJECTED\n\n"
            f"If REJECTED, list what must be fixed before Sprint {sprint + 1}."
        ),
        expected_output=(
            "First line: `VERDICT: APPROVED` or `VERDICT: REJECTED`. "
            "If REJECTED: list of required fixes."
        ),
        agent=team_leader,
        output_file=f"output/backend_gate_sprint_{sprint}.md",
    )


def create_frontend_gate_task(feature_description: str, sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} — Decide if the frontend is ready to proceed to testing.\n\n"
            "The architecture, backend, frontend implementation, and code review are in your context. "
            "The review already inspected the actual files on disk — trust its findings.\n\n"
            "APPROVE if the review shows no Critical issues and at most 2 Major issues. "
            "REJECT otherwise.\n\n"
            "Your Final Answer MUST begin with:\n"
            "VERDICT: APPROVED  or  VERDICT: REJECTED\n\n"
            f"If REJECTED, list what must be fixed before Sprint {sprint + 1}."
        ),
        expected_output=(
            "First line: `VERDICT: APPROVED` or `VERDICT: REJECTED`. "
            "If REJECTED: list of required fixes."
        ),
        agent=team_leader,
        output_file=f"output/frontend_gate_sprint_{sprint}.md",
    )


def create_test_gate_task(feature_description: str, sprint: int = 1) -> Task:
    return Task(
        description=(
            f"Sprint {sprint} — Decide if the test results are acceptable to proceed to DevOps.\n\n"
            "The architecture, implementation, and test results are in your context.\n\n"
            "APPROVE if all tests pass or only Minor failures remain. "
            "REJECT if any Critical test failure exists or core endpoint tests are missing.\n\n"
            "Your Final Answer MUST begin with:\n"
            "VERDICT: APPROVED  or  VERDICT: REJECTED\n\n"
            f"If REJECTED, list what must be fixed before re-testing in Sprint {sprint + 1}."
        ),
        expected_output=(
            "First line: `VERDICT: APPROVED` or `VERDICT: REJECTED`. "
            "If REJECTED: list of required fixes."
        ),
        agent=team_leader,
        output_file=f"output/test_gate_sprint_{sprint}.md",
    )


def create_approval_task(feature_description: str) -> Task:
    return Task(
        description=(
            f"Final approval review for:\n\n{feature_description}\n\n"
            "All deliverables are in your context: architecture, backend, frontend/mobile, "
            "tests, devops, and documentation. "
            "Verify the project is complete and correct against ARCHITECTURE.md.\n\n"
            "Your Final Answer MUST begin with:\n"
            "VERDICT: APPROVED  or  VERDICT: REJECTED\n\n"
            "If REJECTED, list every issue as:\n"
            "[SEVERITY: Critical|Major|Minor] | <area> | <issue> | <required fix>\n\n"
            "If APPROVED, provide a brief summary of what was verified."
        ),
        expected_output=(
            "First line: `VERDICT: APPROVED` or `VERDICT: REJECTED`. "
            "If REJECTED: prioritised issue list. If APPROVED: brief verification summary."
        ),
        agent=team_leader,
        output_file="output/06_approval.md",
    )

