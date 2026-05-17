"""crew/orchestrator.py — Production-grade iterative development cycle.

Implements the 5-phase loop that mirrors a real engineering workflow:

  Phase 1  — Architecture Design  (runs once)
             project_architect designs the full system and writes scaffolding files

  Phase 2a — Backend Sprint Loop  (up to MAX_SPRINTS attempts — independent counter)
             backend_developer  → implements Python backend
             code_reviewer      → audits backend code quality and security
             team_leader gate   → VERDICT: APPROVED → Phase 2b
                                  VERDICT: REJECTED → revise and repeat

  Phase 2b — Frontend Sprint Loop  (up to MAX_SPRINTS attempts — independent counter)
             frontend_developer → implements TypeScript/React Native frontend
             code_reviewer      → audits frontend code quality and security
             team_leader gate   → VERDICT: APPROVED → Phase 3
                                  VERDICT: REJECTED → revise and repeat

  Phase 3  — Test Sprint Loop  (up to MAX_SPRINTS attempts — independent counter)
             test_engineer      → writes and runs test suites
             team_leader gate   → VERDICT: APPROVED → Phase 4
                                  VERDICT: REJECTED → fix code, re-test, repeat

  Phase 4  — Finalisation  (runs once)
             devops_agent  → Dockerfiles, CI/CD, smoke tests
             tech_writer   → README, API docs
             team_leader   → issues final VERDICT: APPROVED / REJECTED

Each gate checkpoint has its own independent MAX_SPRINTS retry budget.
When a gate approves and control moves to the next phase, the sprint counter resets.

main.py uses run_production_cycle() as its entry point.
"""

import itertools

from crewai import Crew, Process

from config.settings import MAX_SPRINTS  # int | str ("critical"/"major"/"minor") | None ("continue")
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
    create_backend_review_task,
    create_frontend_review_task,
    create_backend_gate_task,
    create_frontend_gate_task,
    create_backend_revision_task,
    create_frontend_revision_task,
    create_testing_task,
    create_test_gate_task,
    create_retest_task,
    create_devops_task,
    create_documentation_task,
    create_approval_task,
)


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


def _run_safe(agents: list, tasks: list, label: str = "Task") -> tuple[object, bool]:
    """Like _run() but catches LLM errors.

    Returns (result, success).  On failure, logs a warning and returns ("", False).
    Use for implementation tasks where a crash should not abort the whole pipeline.
    """
    try:
        result = _run(agents, tasks)
        return result, True
    except ValueError as exc:
        _banner(f"⚠  {label} failed (LLM returned empty response): {exc}")
        return "", False
    except Exception as exc:
        _banner(f"⚠  {label} failed unexpectedly: {exc}")
        return "", False


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


def _sprint_iter(max_sprints: int | str | None):
    """Finite range(1, n+1) for integer MAX_SPRINTS; infinite count for None/severity."""
    if isinstance(max_sprints, int):
        return range(1, max_sprints + 1)
    return itertools.count(1)


def _sprint_label(max_sprints: int | str | None) -> str:
    if max_sprints is None:
        return "∞"
    if isinstance(max_sprints, str):
        return f"∞(≤{max_sprints})"
    return str(max_sprints)


_SEVERITY_RANK: dict[str, int] = {"clean": 0, "minor": 1, "major": 2, "critical": 3}


def _max_severity(text: str) -> str:
    """Return the highest severity keyword found in a review/gate output."""
    t = text.lower()
    if "severity: critical" in t or "[critical]" in t:
        return "critical"
    if "severity: major" in t or "[major]" in t:
        return "major"
    if "severity: minor" in t or "[minor]" in t:
        return "minor"
    return "clean"


def _should_exit(verdict: str, review_text: str, max_sprints: int | str | None) -> bool:
    """Return True when the sprint loop exit condition is met.

    - A gate VERDICT: APPROVED always exits the loop, regardless of mode.
    - severity string → also exit when the highest severity in review_text is
                        strictly below the threshold (e.g. "major" → exit when only
                        Minor or CLEAN remain), even when REJECTED.
    - integer / None  → exit only when VERDICT: APPROVED
    """
    if verdict == "APPROVED":
        return True  # gate explicitly approved — always exit
    if isinstance(max_sprints, str):
        severity = _max_severity(review_text)
        return _SEVERITY_RANK[severity] < _SEVERITY_RANK[max_sprints]
    return False


def _extract_output(output_file: str | None) -> None:
    """Extract embedded file blocks from a single agent output .md to disk."""
    if not output_file:
        return
    from utils.file_extractor import extract_files_from_file
    extracted = extract_files_from_file(output_file, overwrite=True)
    if extracted:
        _banner(f"Extracted {len(extracted)} file(s) from {output_file}")


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
    _extract_output(arch_task.output_file)  # extract any fallback === FILE: === blocks

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 2a — Backend Sprint Loop  (independent MAX_SPRINTS counter)
    # ─────────────────────────────────────────────────────────────────────────
    back_feedback = ""
    current_back  = None
    back_approved = False

    for sprint in _sprint_iter(MAX_SPRINTS):
        _banner(f"PHASE 2a — Sprint {sprint}/{_sprint_label(MAX_SPRINTS)}: Backend Implementation")

        if sprint == 1:
            current_back = create_backend_task(feature_request)
        else:
            current_back = create_backend_revision_task(feature_request, back_feedback)

        current_back.context = [arch_task]
        impl_ok: bool
        _, impl_ok = _run_safe(
            [backend_developer], [current_back],
            label=f"Backend Sprint {sprint}",
        )
        _extract_output(current_back.output_file)
        if not impl_ok:
            _banner(f"⚠  Sprint {sprint} backend implementation failed — stopping backend loop")
            break

        back_review = create_backend_review_task(sprint)
        back_review.context = [arch_task, current_back]
        review_out = _run([code_reviewer], [back_review])

        back_gate = create_backend_gate_task(feature_request, sprint)
        back_gate.context = [arch_task, current_back, back_review]
        gate_out = _run([team_leader], [back_gate])

        back_result, back_feedback = _verdict(gate_out)
        _banner(f"Sprint {sprint} Backend Gate  →  {back_result}")

        if _should_exit(back_result, str(review_out) + "\n" + str(gate_out), MAX_SPRINTS):
            back_approved = True
            break

    if not back_approved:
        _banner("WARNING: Max backend sprints reached — continuing with last revision")

    assert current_back is not None  # always assigned in loop body

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 2b — Frontend Sprint Loop  (independent MAX_SPRINTS counter)
    # ─────────────────────────────────────────────────────────────────────────
    front_feedback = ""
    current_front  = None
    front_approved = False

    for sprint in _sprint_iter(MAX_SPRINTS):
        _banner(f"PHASE 2b — Sprint {sprint}/{_sprint_label(MAX_SPRINTS)}: Frontend Implementation")

        if sprint == 1:
            current_front = create_frontend_task(feature_request)
        else:
            current_front = create_frontend_revision_task(feature_request, front_feedback)

        current_front.context = [arch_task, current_back]
        _, impl_ok = _run_safe(
            [frontend_developer], [current_front],
            label=f"Frontend Sprint {sprint}",
        )
        _extract_output(current_front.output_file)
        if not impl_ok:
            _banner(f"⚠  Sprint {sprint} frontend implementation failed — stopping frontend loop")
            break

        front_review = create_frontend_review_task(sprint)
        front_review.context = [arch_task, current_back, current_front]
        review_out = _run([code_reviewer], [front_review])

        front_gate = create_frontend_gate_task(feature_request, sprint)
        front_gate.context = [arch_task, current_back, current_front, front_review]
        gate_out = _run([team_leader], [front_gate])

        front_result, front_feedback = _verdict(gate_out)
        _banner(f"Sprint {sprint} Frontend Gate  →  {front_result}")

        if _should_exit(front_result, str(review_out) + "\n" + str(gate_out), MAX_SPRINTS):
            front_approved = True
            break

    if not front_approved:
        _banner("WARNING: Max frontend sprints reached — continuing with last revision")

    assert current_front is not None  # always assigned in loop body

    # ─────────────────────────────────────────────────────────────────────────
    # Phase 3 — Test loop
    # ─────────────────────────────────────────────────────────────────────────
    test_feedback = ""
    current_test  = None
    test_approved = False

    for sprint in _sprint_iter(MAX_SPRINTS):
        _banner(f"PHASE 3 — Sprint {sprint}/{_sprint_label(MAX_SPRINTS)}: Testing")

        if sprint > 1:
            # Apply code fixes before re-running the tests
            _banner(f"Phase 3 Sprint {sprint} — Applying code fixes")
            assert current_test is not None  # set in previous iteration
            fix_back  = create_backend_revision_task(feature_request, test_feedback)
            fix_front = create_frontend_revision_task(feature_request, test_feedback)
            fix_back.context  = [arch_task, current_test]
            fix_front.context = [arch_task, current_test, fix_back]
            _run([backend_developer, frontend_developer], [fix_back, fix_front])
            _extract_output(fix_back.output_file)
            _extract_output(fix_front.output_file)

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

        if _should_exit(test_result, str(gate_out), MAX_SPRINTS):
            test_approved = True
            break

    if not test_approved:
        _banner("WARNING: Max test sprints reached — continuing with latest code")

    assert current_test is not None  # always assigned in loop body

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
