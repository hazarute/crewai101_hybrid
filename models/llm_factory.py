"""
models/llm_factory.py — LLM instantiation for Hybrid AI architecture.

  Cloud LLMs (langchain_openai)
    ─ architect_llm   → project_architect  (system design)
    ─ code_review_llm → code_reviewer      (OWASP analysis + review gate)
    ─ leader_llm      → team_leader        (VERDICT quality gates)
    Each agent has its own configurable model; all fall back to the base
    OPENROUTER_CLOUD_MODEL / OPENAI_MODEL_NAME when no override is set.

  Local LLMs (langchain_community / ChatOpenAI via OpenRouter)
    ─ backend_llm, frontend_llm, tester_llm, reviewer_llm, devops_llm
    When USE_OPENROUTER_LOCAL=true all workers share OPENROUTER_LOCAL_MODEL.

OpenRouter support (independent flags, can mix-and-match):
  USE_OPENROUTER_CLOUD=true  → Cloud agents use OpenRouter
  USE_OPENROUTER_LOCAL=true  → Worker agents use OpenRouter
"""

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama

from config.settings import (
    OPENAI_API_KEY,
    OPENAI_API_BASE,
    CLOUD_MODEL_ARCHITECT,
    CLOUD_MODEL_REVIEWER,
    CLOUD_MODEL_LEADER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL_BACKEND,
    OLLAMA_MODEL_FRONTEND,
    OLLAMA_MODEL_TESTER,
    OLLAMA_MODEL_REVIEWER,
    OLLAMA_MODEL_DEVOPS,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    USE_OPENROUTER_CLOUD,
    OPENROUTER_CLOUD_MODEL_ARCHITECT,
    OPENROUTER_CLOUD_MODEL_REVIEWER,
    OPENROUTER_CLOUD_MODEL_LEADER,
    USE_OPENROUTER_LOCAL,
    OPENROUTER_LOCAL_MODEL_BACKEND,
    OPENROUTER_LOCAL_MODEL_FRONTEND,
    OPENROUTER_LOCAL_MODEL_TESTER,
    OPENROUTER_LOCAL_MODEL_REVIEWER,
    OPENROUTER_LOCAL_MODEL_DEVOPS,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    USE_DEEPSEEK_CLOUD,
    DEEPSEEK_CLOUD_MODEL_ARCHITECT,
    DEEPSEEK_CLOUD_MODEL_REVIEWER,
    DEEPSEEK_CLOUD_MODEL_LEADER,
    USE_DEEPSEEK_LOCAL,
    DEEPSEEK_LOCAL_MODEL_BACKEND,
    DEEPSEEK_LOCAL_MODEL_FRONTEND,
    DEEPSEEK_LOCAL_MODEL_TESTER,
    DEEPSEEK_LOCAL_MODEL_REVIEWER,
    DEEPSEEK_LOCAL_MODEL_DEVOPS,
)


def _normalize_openrouter_model(model_name: str) -> str:
    model_name = model_name.strip()
    if not model_name:
        return model_name

    known_prefixes = (
        "openrouter/",
        "openai/",
        "anthropic/",
        "google/",
        "azure/",
        "huggingface/",
        "gpt4all/",
        "llama/",
    )

    if model_name.startswith(known_prefixes):
        return model_name

    return f"openrouter/{model_name}"


def _normalize_openai_model(model_name: str) -> str:
    name = model_name.strip()
    if not name:
        return name

    known_prefixes = (
        "openai/",
        "openrouter/",
        "anthropic/",
        "google/",
        "azure/",
        "huggingface/",
        "gpt4all/",
        "llama/",
    )

    if name.startswith(known_prefixes):
        return name
    return f"openai/{name}"


def get_cloud_llm(openrouter_model: str, openai_model: str, deepseek_model: str) -> ChatOpenAI:
    """
    Base cloud LLM factory.
    Priority: OpenRouter → Deepseek → OpenAI → OpenRouter fallback → Deepseek fallback.
    Each provider is only used when explicitly enabled via its USE_* flag or as last resort.
    """
    if USE_OPENROUTER_CLOUD and OPENROUTER_API_KEY:
        return ChatOpenAI(
            model=_normalize_openrouter_model(openrouter_model),
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=0.2,
        )

    if USE_DEEPSEEK_CLOUD and DEEPSEEK_API_KEY:
        return ChatOpenAI(
            model=deepseek_model,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=0.2,
        )

    if OPENAI_API_KEY:
        return ChatOpenAI(
            model=_normalize_openai_model(openai_model),
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE or None,
            temperature=0.2,
        )

    if OPENROUTER_API_KEY:
        return ChatOpenAI(
            model=_normalize_openrouter_model(openrouter_model),
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=0.2,
        )

    if DEEPSEEK_API_KEY:
        return ChatOpenAI(
            model=deepseek_model,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=0.2,
        )

    raise RuntimeError(
        "No cloud LLM configured. Set OPENAI_API_KEY, DEEPSEEK_API_KEY, or OPENROUTER_API_KEY in .env."
    )


def get_architect_llm() -> ChatOpenAI:
    """Cloud LLM for project_architect (system design & scaffolding)."""
    return get_cloud_llm(OPENROUTER_CLOUD_MODEL_ARCHITECT, CLOUD_MODEL_ARCHITECT, DEEPSEEK_CLOUD_MODEL_ARCHITECT)


def get_code_review_llm() -> ChatOpenAI:
    """Cloud LLM for code_reviewer (OWASP analysis + review gate)."""
    return get_cloud_llm(OPENROUTER_CLOUD_MODEL_REVIEWER, CLOUD_MODEL_REVIEWER, DEEPSEEK_CLOUD_MODEL_REVIEWER)


def get_leader_llm() -> ChatOpenAI:
    """Cloud LLM for team_leader (VERDICT quality gates + final approval)."""
    return get_cloud_llm(OPENROUTER_CLOUD_MODEL_LEADER, CLOUD_MODEL_LEADER, DEEPSEEK_CLOUD_MODEL_LEADER)


def get_local_llm(ollama_model: str, openrouter_model: str, deepseek_model: str) -> ChatOpenAI | ChatOllama:
    """
    Returns the LLM used by a worker agent.
    Priority: OpenRouter → Deepseek → Ollama → OpenRouter fallback → Deepseek fallback.
    """
    if USE_OPENROUTER_LOCAL and OPENROUTER_API_KEY:
        return ChatOpenAI(
            model=_normalize_openrouter_model(openrouter_model),
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=0.3,
        )

    if USE_DEEPSEEK_LOCAL and DEEPSEEK_API_KEY:
        return ChatOpenAI(
            model=deepseek_model,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=0.3,
        )

    if OLLAMA_BASE_URL:
        return ChatOllama(
            model=ollama_model,
            base_url=OLLAMA_BASE_URL,
            temperature=0.3,
        )

    if OPENROUTER_API_KEY:
        return ChatOpenAI(
            model=_normalize_openrouter_model(openrouter_model),
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            temperature=0.3,
        )

    if DEEPSEEK_API_KEY:
        return ChatOpenAI(
            model=deepseek_model,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=0.3,
        )

    raise RuntimeError(
        "No worker LLM configured. Set OLLAMA_BASE_URL, DEEPSEEK_API_KEY, or OPENROUTER_API_KEY in .env."
    )


def get_cloud_provider_name() -> str:
    if USE_OPENROUTER_CLOUD and OPENROUTER_API_KEY:
        return "OpenRouter"
    if USE_DEEPSEEK_CLOUD and DEEPSEEK_API_KEY:
        return "Deepseek"
    if OPENAI_API_KEY:
        return "OpenAI"
    if OPENROUTER_API_KEY:
        return "OpenRouter"
    if DEEPSEEK_API_KEY:
        return "Deepseek"
    return "None"


def get_worker_provider_name() -> str:
    if USE_OPENROUTER_LOCAL and OPENROUTER_API_KEY:
        return "OpenRouter"
    if USE_DEEPSEEK_LOCAL and DEEPSEEK_API_KEY:
        return "Deepseek"
    if OLLAMA_BASE_URL:
        return "Ollama (local)"
    if OPENROUTER_API_KEY:
        return "OpenRouter"
    if DEEPSEEK_API_KEY:
        return "Deepseek"
    return "None"


# ── Pre-built singleton instances ─────────────────────────────────────────────
# Cloud agents — one configurable model per agent
architect_llm   = get_architect_llm()    # project_architect
code_review_llm = get_code_review_llm()  # code_reviewer
leader_llm      = get_leader_llm()       # team_leader

# Local worker agents
backend_llm  = get_local_llm(OLLAMA_MODEL_BACKEND,  OPENROUTER_LOCAL_MODEL_BACKEND,  DEEPSEEK_LOCAL_MODEL_BACKEND)
frontend_llm = get_local_llm(OLLAMA_MODEL_FRONTEND, OPENROUTER_LOCAL_MODEL_FRONTEND, DEEPSEEK_LOCAL_MODEL_FRONTEND)
tester_llm   = get_local_llm(OLLAMA_MODEL_TESTER,   OPENROUTER_LOCAL_MODEL_TESTER,   DEEPSEEK_LOCAL_MODEL_TESTER)
reviewer_llm = get_local_llm(OLLAMA_MODEL_REVIEWER, OPENROUTER_LOCAL_MODEL_REVIEWER, DEEPSEEK_LOCAL_MODEL_REVIEWER)  # tech_writer
devops_llm   = get_local_llm(OLLAMA_MODEL_DEVOPS,   OPENROUTER_LOCAL_MODEL_DEVOPS,   DEEPSEEK_LOCAL_MODEL_DEVOPS)

CLOUD_PROVIDER_NAME = get_cloud_provider_name()
WORKER_PROVIDER_NAME = get_worker_provider_name()
