"""crew/orchestrator.py — Production-grade iterative development cycle.

Implements the 4-phase loop that mirrors a real engineering workflow:

  Phase 1 — Architecture Design  (runs once)
             project_architect designs the full system and writes scaffolding files

  Phase 2 — Implementation Sprint Loop  (max MAX_SPRINTS iterations)
             backend_developer  → implements Python backend
             frontend_developer → implements TypeScript frontend
             code_reviewer      → audits code quality and security
             team_leader gate   → VERDICT: APPROVED → Phase 3
                                  VERDICT: REJECTED → revise and repeat

  Phase 3 — Test Sprint Loop  (max MAX_SPRINTS iterations)
             test_engineer      → writes and runs test suites
             team_leader gate   → VERDICT: APPROVED → Phase 4
                                  VERDICT: REJECTED → fix code, re-test, repeat

  Phase 4 — Finalisation  (runs once)
             devops_agent  → Dockerfiles, CI/CD, smoke tests
             tech_writer   → README, API docs
             team_leader   → issues final VERDICT: APPROVED / REJECTED

main.py uses run_production_cycle() as its entry point.
build_crew() in hybrid_crew.py remains available for simple / debug runs.
"""

from crewai import Crew, Process

from agents import (
    project_architect,
    backend_developer,
    frontend_developer,
    code_reviewer,
    test_engineer,
    devops_agent,
    tech_writer,
    team_leader,
)
from tasks import (
    create_architecture_task,
    create_backend_task,
    create_frontend_task,
    create_code_review_task,
    create_dev_gate_task,
    create_backend_revision_task,
    create_frontend_revision_task,
    create_testing_task,
    create_test_gate_task,
    create_retest_task,
    create_devops_task,
    create_documentation_task,
    create_approval_task,
)

MAX_SPRINTS = 3  # maximum rework iterations per phase before moving on


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(agents: list, tasks: list) -> object:
    """Spin up a minimal sequential crew, run it, and return the kickoff result."""
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=False,
    )
    return crew.kickoff()


def _verdict(output) -> tuple[str, str]:
    """Parse VERDICT: APPROVED / REJECTED from an agent output string.

    Returns (verdict, feedback_text).
    Defaults to APPROVED when neither keyword is present.
    """
    text = str(output)
    if "VERDICT: REJECTED" in text:
        idx = text.find("VERDICT: REJECTED")
        return "REJECTED", text[idx:].strip()
    return "APPROVED", ""


def _banner(msg: str) -> None:
    print(f"\n{'━' * 64}\n  {msg}\n{'━' * 64}")


# ── Production cycle ───────────────────────────────────────────────────────────

def run_production_cycle(feature_request: str) -> str:
    """Runs the full 4-phase production-grade development cycle.

    Returns the Team Leader's final approval text.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 1 — Architecture  (once)
    # ─────────────────────────────────────────────────────────────────────────
    _banner("PHASE 1 — Architecture Design")
    arch_task = create_architecture_task(feature_request)
    _run([project_architect], [arch_task])

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 2 — Implementation + Code Review loop
    # ─────────────────────────────────────────────────────────────────────────
    dev_feedback  = ""
    current_back  = None
    current_front = None
    dev_approved  = False

    for sprint in range(1, MAX_SPRINTS + 1):
        _banner(f"PHASE 2 — Sprint {sprint}/{MAX_SPRINTS}: Implementation & Code Review")

        if sprint == 1:
            current_back  = create_backend_task(feature_request)
            current_front = create_frontend_task(feature_request)
        else:
            current_back  = create_backend_revision_task(feature_request, dev_feedback)
            current_front = create_frontend_revision_task(feature_request, dev_feedback)

        current_back.context  = [arch_task]
        current_front.context = [arch_task, current_back]

        review = create_code_review_task(sprint)
        review.context = [arch_task, current_back, current_front]

        _run(
            [backend_developer, frontend_developer, code_reviewer],
            [current_back, current_front, review],
        )

        gate = create_dev_gate_task(feature_request, sprint)
        gate.context = [arch_task, current_back, current_front, review]
        gate_out = _run([team_leader], [gate])

        dev_result, dev_feedback = _verdict(gate_out)
        _banner(f"Sprint {sprint} Code Review Gate  →  {dev_result}")

        if dev_result == "APPROVED":
            dev_approved = True
            break

    if not dev_approved:
        _banner("WARNING: Max code-review sprints reached — continuing with last revision")

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 3 — Test loop
    # ─────────────────────────────────────────────────────────────────────────
    test_feedback = ""
    current_test  = None
    test_approved = False

    for sprint in range(1, MAX_SPRINTS + 1):
        _banner(f"PHASE 3 — Sprint {sprint}/{MAX_SPRINTS}: Testing")

        if sprint > 1:
            # Apply code fixes before re-running the tests
            _banner(f"Phase 3 Sprint {sprint} — Applying code fixes")
            fix_back  = create_backend_revision_task(feature_request, test_feedback)
            fix_front = create_frontend_revision_task(feature_request, test_feedback)
            fix_back.context  = [arch_task, current_test]
            fix_front.context = [arch_task, current_test, fix_back]
            _run([backend_developer, frontend_developer], [fix_back, fix_front])

            # Update "current" implementation references
            current_back  = fix_back
            current_front = fix_front

            current_test = create_retest_task(test_feedback)
        else:
            current_test = create_testing_task()

        current_test.context = [arch_task, current_back, current_front]
        _run([test_engineer], [current_test])

        test_gate = create_test_gate_task(feature_request, sprint)
        test_gate.context = [arch_task, current_back, current_front, current_test]
        gate_out = _run([team_leader], [test_gate])

        test_result, test_feedback = _verdict(gate_out)
        _banner(f"Sprint {sprint} Test Gate  →  {test_result}")

        if test_result == "APPROVED":
            test_approved = True
            break

    if not test_approved:
        _banner("WARNING: Max test sprints reached — continuing with latest code")

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 4 — Finalisation  (once)
    # ─────────────────────────────────────────────────────────────────────────
    _banner("PHASE 4 — DevOps Configuration & Documentation")
    devops = create_devops_task(feature_request)
    docs   = create_documentation_task(feature_request)
    devops.context = [arch_task, current_back, current_front, current_test]
    docs.context   = [arch_task, current_back, current_front, devops]
    _run([devops_agent, tech_writer], [devops, docs])

    # ─────────────────────────────────────────────────────────────────────────
    # Final Approval
    # ─────────────────────────────────────────────────────────────────────────
    _banner("FINAL APPROVAL — Team Leader")
    approval = create_approval_task(feature_request)
    approval.context = [
        arch_task, current_back, current_front,
        current_test, devops, docs,
    ]
    final = _run([team_leader], [approval])

    return str(final)
