"""
utils/file_extractor.py — Post-run project file extractor.

Scans every .md file in the output/ directory for file content embedded by
agents that could not use FileWriterTool directly.

Supported formats
-----------------
Format 1 — Explicit markers (preferred, agents are instructed to use this):

    === FILE: projects/<slug>/relative/path/to/file ===
    ```lang
    <content>
    ```
    === END FILE ===

Format 2 — Markdown header fallback (matches common LLM output patterns):

    ### `projects/<slug>/relative/path/to/file`
    ```lang
    <content>
    ```

Files already written by FileWriterTool will be on disk and are skipped if
their path already exists (no overwrite).
"""

import re
from pathlib import Path

# ── Regex patterns ────────────────────────────────────────────────────────────

# Explicit === FILE: path === ... === END FILE === markers
_EXPLICIT_RE = re.compile(
    r"={3} FILE: (.+?) ={3}\n```[^\n]*\n(.*?)\n```\n={3} END FILE ={3}",
    re.DOTALL,
)

# Markdown "### `path`" style header followed by a fenced code block
_MD_HEADER_RE = re.compile(
    r"###\s+`(.+?)`\s*\n```[^\n]*\n(.*?)\n```",
    re.DOTALL,
)

# Plain markdown "**`path`**" or "**path**" bold header before a code block
_BOLD_HEADER_RE = re.compile(
    r"\*\*`?(projects/[^\s`*]+)`?\*\*\s*\n```[^\n]*\n(.*?)\n```",
    re.DOTALL,
)


def _iter_matches(content: str):
    """Yield (file_path, file_content) tuples from all supported formats."""
    seen_spans: list[tuple[int, int]] = []

    for pattern in (_EXPLICIT_RE, _MD_HEADER_RE, _BOLD_HEADER_RE):
        for m in pattern.finditer(content):
            # Skip if this span overlaps a previous match (avoid double-writing)
            start, end = m.span()
            if any(s <= start < e or s < end <= e for s, e in seen_spans):
                continue
            seen_spans.append((start, end))
            file_path = m.group(1).strip()
            file_content = m.group(2)
            yield file_path, file_content


def extract_files_from_output(
    output_dir: str = "output",
    overwrite: bool = False,
    dry_run: bool = False,
) -> list[str]:
    """
    Scan all .md files in *output_dir*, extract embedded file blocks,
    and write them to disk.

    Args:
        output_dir: Directory containing agent output .md files.
        overwrite:  If False (default), skip files that already exist on disk.
        dry_run:    If True, only report what would be written without writing.

    Returns:
        List of file paths that were (or would be) written.
    """
    extracted: list[str] = []
    output_path = Path(output_dir)

    if not output_path.exists():
        return extracted

    for md_file in sorted(output_path.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")

        for file_path, file_content in _iter_matches(content):
            dest = Path(file_path)

            if dest.exists() and not overwrite:
                print(f"  [extractor] skip (exists): {file_path}")
                continue

            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(file_content, encoding="utf-8")

            action = "dry-run" if dry_run else "wrote"
            print(f"  [extractor] {action}: {file_path}")
            extracted.append(file_path)

    return extracted
