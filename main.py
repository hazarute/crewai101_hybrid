"""
main.py — Hybrid AI Software Agency entry point.

Usage:
    python main.py

    Override the feature request via environment variable:
        FEATURE_REQUEST="Build a URL shortener API" python main.py

    Or set FEATURE_REQUEST in your .env file.
"""

from pathlib import Path

from config.settings import DEFAULT_FEATURE_REQUEST
from crew.orchestrator import run_production_cycle
from models.llm_factory import CLOUD_PROVIDER_NAME, WORKER_PROVIDER_NAME
from utils.file_extractor import extract_files_from_output


def main() -> None:
    feature_request = DEFAULT_FEATURE_REQUEST

    print("\n" + "=" * 64)
    print("  Hybrid AI Software Agency")
    print(f"  Architect: {CLOUD_PROVIDER_NAME}  |  Workers: {WORKER_PROVIDER_NAME}")
    print("=" * 64)
    print(f"\nFeature Request:\n{feature_request}\n")
    print("Starting crew...\n")

    result = run_production_cycle(feature_request)

    # ── Extract project files from output markdown (fallback for agents that
    #    produced === FILE: === markers instead of using FileWriterTool) ───────
    print("\n" + "=" * 64)
    print("  Extracting Project Files from Output Markdown")
    print("=" * 64)
    extracted = extract_files_from_output()
    if extracted:
        print(f"\n  {len(extracted)} file(s) extracted from output markdown:")
        for f in extracted:
            print(f"    ✓ {f}")
    else:
        print("\n  All files were written directly by agents (FileWriterTool).")

    # ── Read team_leader's verdict from output/06_approval.md ──────────────
    approval_file = Path("output/06_approval.md")
    if approval_file.exists():
        approval_text = approval_file.read_text(encoding="utf-8")
        if "VERDICT: APPROVED" in approval_text:
            print("\n" + "=" * 64)
            print("  ✅  VERDICT: APPROVED — Project is ready to ship.")
            print("=" * 64)
        elif "VERDICT: REJECTED" in approval_text:
            print("\n" + "=" * 64)
            print("  ❌  VERDICT: REJECTED — Review output/06_approval.md for required fixes.")
            print("=" * 64)

    print("\n" + "=" * 64)
    print("  Final Deliverable")
    print("=" * 64)
    print(result)


if __name__ == "__main__":
    main()

