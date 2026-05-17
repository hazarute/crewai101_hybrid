"""
utils/tools.py — Shared tool factories for CrewAI agents.

DirectorySearchTool uses OpenAI embeddings by default (via embedchain/chromadb).
When OPENAI_API_KEY is unset or points to a provider that doesn't support
/v1/embeddings (e.g. Deepseek), the tool fails with APIStatusError.

make_directory_search_tool() bypasses the cloud embedding dependency entirely
by using chromadb's built-in ONNXMiniLM_L6_V2 model — a local, offline,
384-dimensional sentence embedding model.  No API key required.

The tool is pre-configured to search the workspace-relative `projects/` directory
so agents only need to supply a search query — no path argument needed.

SafeFileWriterTool — drop-in replacement for FileWriterTool that automatically
creates parent directories before writing a file, preventing silent failures when
a subdirectory (e.g. app/routes/) does not yet exist on disk.
"""

import os
from pathlib import Path

from crewai_tools import DirectorySearchTool, FileWriterTool
from crewai_tools.adapters.embedchain_adapter import EmbedchainAdapter
from embedchain import App
from embedchain.embedder.base import BaseEmbedder
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from pydantic import model_validator

# Absolute path to the projects/ output folder (workspace root / projects)
_PROJECTS_DIR: str = str(Path(__file__).resolve().parent.parent / "projects")


class SafeFileWriterTool(FileWriterTool):
    """
    FileWriterTool that creates all parent directories before writing.

    FileWriterTool silently fails (or raises) when the target subdirectory does not
    yet exist on disk (e.g. writing `app/routes/api.py` when `app/routes/` has never
    been created).  This subclass patches `_run` to call `os.makedirs` first so that
    nested directories are created transparently.
    """

    name: str = "File Writer Tool"
    description: str = (
        "Writes content to a file. Automatically creates any missing parent "
        "directories. Accepts ONE file per call as a plain dict: "
        '{"filename": "...", "directory": "...", "content": "..."}.'
    )

    def _run(self, **kwargs) -> str:  # type: ignore[override]
        directory: str = kwargs.get("directory", "")
        filename: str = kwargs.get("filename", "")
        # Create the full parent path (includes any subdirs embedded in filename)
        full_path = Path(directory or ".") / (filename or "")
        os.makedirs(full_path.parent, exist_ok=True)
        # Always allow overwriting — revision tasks must be able to fix existing files
        kwargs = dict(kwargs)
        kwargs["overwrite"] = True
        return super()._run(**kwargs)


def make_directory_search_tool() -> DirectorySearchTool:
    """
    Returns a DirectorySearchTool pre-pointed at the workspace `projects/` directory,
    backed by chromadb's local ONNX embedding model (all-MiniLM-L6-v2, 384 dims).

    - Agents only provide a search query; no directory argument needed.
    - Works with any LLM provider — no OPENAI_API_KEY or external embedding API.
    - Relative path errors are eliminated because the directory is resolved at
      import time to an absolute path.
    """
    # Ensure the directory exists before DirectorySearchTool tries to index it.
    # On a fresh run projects/ won't exist yet and the tool raises ValueError.
    Path(_PROJECTS_DIR).mkdir(parents=True, exist_ok=True)

    ef = DefaultEmbeddingFunction()          # ONNXMiniLM_L6_V2, fully local
    embedder = BaseEmbedder()
    embedder.set_embedding_fn(ef)
    embedder.set_vector_dimension(384)
    app = App(embedding_model=embedder)
    adapter = EmbedchainAdapter(embedchain_app=app)
    return DirectorySearchTool(directory=_PROJECTS_DIR, adapter=adapter)
