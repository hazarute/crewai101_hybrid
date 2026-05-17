"""tasks/_shared.py — Shared constants reused across all task description modules."""

_FILE_FORMAT_HELP = (
    "If FileWriterTool is unavailable, embed each file using this EXACT format:\n"
    "=== FILE: projects/<slug>/relative/path/to/file ===\n"
    "```lang\n"
    "<file content>\n"
    "```\n"
    "=== END FILE ==="
)

_FILE_WRITER_RULE = (
    "FileWriterTool accepts EXACTLY ONE file per call — always a plain dict:\n"
    "  {\"filename\": \"file.py\", \"directory\": \"projects/<slug>/...\", \"content\": \"...\"}\n"
    "NEVER pass a JSON array or list of files in one call — it will fail every time."
)
