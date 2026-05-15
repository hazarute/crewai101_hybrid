"""
config/settings.py — Central configuration loader.

All environment variables are read here and exported as typed constants.
The rest of the application imports from this module instead of calling
os.getenv() directly, making configuration changes easy to track.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Cloud LLM (Team Leader / Orchestrator) ───────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "").strip()
OPENAI_ENABLED: bool = bool(OPENAI_API_KEY)
CLOUD_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")

# ── Local LLM (Worker Agents via Ollama) ─────────────────────────────────────
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
OLLAMA_ENABLED: bool = bool(OLLAMA_BASE_URL)

OLLAMA_MODEL_BACKEND: str  = os.getenv("OLLAMA_MODEL_BACKEND",  "llama3")
OLLAMA_MODEL_FRONTEND: str = os.getenv("OLLAMA_MODEL_FRONTEND", "llama3")
OLLAMA_MODEL_TESTER: str   = os.getenv("OLLAMA_MODEL_TESTER",   "mistral")
OLLAMA_MODEL_REVIEWER: str = os.getenv("OLLAMA_MODEL_REVIEWER", "mistral")
OLLAMA_MODEL_DEVOPS: str   = os.getenv("OLLAMA_MODEL_DEVOPS",   "llama3")

# ── OpenRouter (optional — overrides OpenAI / Ollama when enabled) ─────────────
OPENROUTER_API_KEY: str      = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_ENABLED: bool    = bool(OPENROUTER_API_KEY)
OPENROUTER_BASE_URL: str     = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")

# When OpenRouter is enabled but OpenAI is not configured, use OpenRouter as
# a drop-in OpenAI-compatible backend for embeddings and any library that
# uses OPENAI_API_KEY / OPENAI_API_BASE.
if OPENROUTER_ENABLED and not OPENAI_ENABLED:
    os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
    os.environ["OPENAI_API_BASE"] = OPENROUTER_BASE_URL

# Set to "true" to route the Cloud Orchestrator through OpenRouter when available
USE_OPENROUTER_CLOUD: bool   = os.getenv("USE_OPENROUTER_CLOUD", "false").lower() == "true" and OPENROUTER_ENABLED
OPENROUTER_CLOUD_MODEL: str  = os.getenv("OPENROUTER_CLOUD_MODEL", "openai/gpt-4o-mini")

# Per-agent cloud model overrides — each defaults to OPENROUTER_CLOUD_MODEL.
# Set in .env only if you want a specific agent to use a different model.
OPENROUTER_CLOUD_MODEL_ARCHITECT: str = os.getenv("OPENROUTER_CLOUD_MODEL_ARCHITECT", OPENROUTER_CLOUD_MODEL)
OPENROUTER_CLOUD_MODEL_REVIEWER:  str = os.getenv("OPENROUTER_CLOUD_MODEL_REVIEWER",  OPENROUTER_CLOUD_MODEL)
OPENROUTER_CLOUD_MODEL_LEADER:    str = os.getenv("OPENROUTER_CLOUD_MODEL_LEADER",    OPENROUTER_CLOUD_MODEL)

# Per-agent OpenAI model overrides — each defaults to CLOUD_MODEL_NAME (OPENAI_MODEL_NAME).
CLOUD_MODEL_ARCHITECT: str = os.getenv("CLOUD_MODEL_ARCHITECT", CLOUD_MODEL_NAME)
CLOUD_MODEL_REVIEWER:  str = os.getenv("CLOUD_MODEL_REVIEWER",  CLOUD_MODEL_NAME)
CLOUD_MODEL_LEADER:    str = os.getenv("CLOUD_MODEL_LEADER",    CLOUD_MODEL_NAME)

# Set to "true" to route all Worker agents through OpenRouter when available
USE_OPENROUTER_LOCAL: bool   = os.getenv("USE_OPENROUTER_LOCAL", "false").lower() == "true" and OPENROUTER_ENABLED
OPENROUTER_LOCAL_MODEL: str  = os.getenv("OPENROUTER_LOCAL_MODEL", "openai/gpt-4o-mini")

# Per-agent OpenRouter local model overrides — each defaults to OPENROUTER_LOCAL_MODEL.
# Set in .env only if you want a specific worker to use a different model.
OPENROUTER_LOCAL_MODEL_BACKEND:  str = os.getenv("OPENROUTER_LOCAL_MODEL_BACKEND",  OPENROUTER_LOCAL_MODEL)
OPENROUTER_LOCAL_MODEL_FRONTEND: str = os.getenv("OPENROUTER_LOCAL_MODEL_FRONTEND", OPENROUTER_LOCAL_MODEL)
OPENROUTER_LOCAL_MODEL_TESTER:   str = os.getenv("OPENROUTER_LOCAL_MODEL_TESTER",   OPENROUTER_LOCAL_MODEL)
OPENROUTER_LOCAL_MODEL_REVIEWER: str = os.getenv("OPENROUTER_LOCAL_MODEL_REVIEWER", OPENROUTER_LOCAL_MODEL)  # tech_writer
OPENROUTER_LOCAL_MODEL_DEVOPS:   str = os.getenv("OPENROUTER_LOCAL_MODEL_DEVOPS",   OPENROUTER_LOCAL_MODEL)

# ── Deepseek (optional — OpenAI-uyumlu, ücretli/ücretsiz planlar) ─────────────
# Deepseek, OpenAI API'siyle tam uyumludur; OPENAI_API_KEY'den bağımsız kendi
# anahtarıyla yapılandırılabilir.  https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY: str       = os.getenv("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_ENABLED: bool      = bool(DEEPSEEK_API_KEY)
DEEPSEEK_BASE_URL: str      = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")

# Set to "true" to route the Cloud Orchestrator through Deepseek when available
USE_DEEPSEEK_CLOUD: bool    = os.getenv("USE_DEEPSEEK_CLOUD", "false").lower() == "true" and DEEPSEEK_ENABLED
DEEPSEEK_CLOUD_MODEL: str   = os.getenv("DEEPSEEK_CLOUD_MODEL", "deepseek-chat")

# Per-agent cloud model overrides — each defaults to DEEPSEEK_CLOUD_MODEL.
DEEPSEEK_CLOUD_MODEL_ARCHITECT: str = os.getenv("DEEPSEEK_CLOUD_MODEL_ARCHITECT", DEEPSEEK_CLOUD_MODEL)
DEEPSEEK_CLOUD_MODEL_REVIEWER:  str = os.getenv("DEEPSEEK_CLOUD_MODEL_REVIEWER",  DEEPSEEK_CLOUD_MODEL)
DEEPSEEK_CLOUD_MODEL_LEADER:    str = os.getenv("DEEPSEEK_CLOUD_MODEL_LEADER",    DEEPSEEK_CLOUD_MODEL)

# Set to "true" to route all Worker agents through Deepseek when available
USE_DEEPSEEK_LOCAL: bool    = os.getenv("USE_DEEPSEEK_LOCAL", "false").lower() == "true" and DEEPSEEK_ENABLED
DEEPSEEK_LOCAL_MODEL: str   = os.getenv("DEEPSEEK_LOCAL_MODEL", "deepseek-chat")

# Per-agent local model overrides — each defaults to DEEPSEEK_LOCAL_MODEL.
DEEPSEEK_LOCAL_MODEL_BACKEND:  str = os.getenv("DEEPSEEK_LOCAL_MODEL_BACKEND",  DEEPSEEK_LOCAL_MODEL)
DEEPSEEK_LOCAL_MODEL_FRONTEND: str = os.getenv("DEEPSEEK_LOCAL_MODEL_FRONTEND", DEEPSEEK_LOCAL_MODEL)
DEEPSEEK_LOCAL_MODEL_TESTER:   str = os.getenv("DEEPSEEK_LOCAL_MODEL_TESTER",   DEEPSEEK_LOCAL_MODEL)
DEEPSEEK_LOCAL_MODEL_REVIEWER: str = os.getenv("DEEPSEEK_LOCAL_MODEL_REVIEWER", DEEPSEEK_LOCAL_MODEL)  # tech_writer
DEEPSEEK_LOCAL_MODEL_DEVOPS:   str = os.getenv("DEEPSEEK_LOCAL_MODEL_DEVOPS",   DEEPSEEK_LOCAL_MODEL)

# ── Runtime feature request (can be overridden via env) ──────────────────────
# Priority: FEATURE_REQUEST_FILE (path to a .md / .txt file) >
#           FEATURE_REQUEST (inline text) > built-in default.
def _load_feature_request() -> str:
    file_path = os.getenv("FEATURE_REQUEST_FILE", "").strip()
    if file_path:
        from pathlib import Path as _Path
        p = _Path(file_path)
        if p.is_file():
            return p.read_text(encoding="utf-8").strip()
        raise FileNotFoundError(
            f"FEATURE_REQUEST_FILE points to a non-existent file: {file_path}"
        )
    return os.getenv(
        "FEATURE_REQUEST",
        (
            "Build a simple REST API endpoint that accepts a JSON payload with "
            "a 'message' field and returns it reversed, along with a React "
            "component that calls this endpoint and displays the result."
        ),
    )

DEFAULT_FEATURE_REQUEST: str = _load_feature_request()
