"""Configuration for the LLM Council."""

import os
import json
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Council members - list of OpenRouter model identifiers
# Override via COUNCIL_MODELS env var as JSON array
DEFAULT_COUNCIL_MODELS = [
    "anthropic/claude-sonnet-4.5",
    "deepseek/deepseek-chat-v3.1",
    "openai/gpt-5.1",
]
env_models = os.getenv("COUNCIL_MODELS")
if env_models:
    try:
        COUNCIL_MODELS = json.loads(env_models)
    except json.JSONDecodeError:
        COUNCIL_MODELS = DEFAULT_COUNCIL_MODELS
else:
    COUNCIL_MODELS = DEFAULT_COUNCIL_MODELS

# Chairman model - synthesizes final response
DEFAULT_CHAIRMAN_MODEL = "google/gemini-3-pro-image"
CHAIRMAN_MODEL = os.getenv("CHAIRMAN_MODEL", DEFAULT_CHAIRMAN_MODEL)

# LiteLLM proxy URL (optional) — overrides OpenRouter when set
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL")

# API endpoint — uses LiteLLM proxy if configured, else OpenRouter direct
OPENROUTER_API_URL = LITELLM_PROXY_URL if LITELLM_PROXY_URL else "https://openrouter.ai/api/v1/chat/completions"

# API key to use for requests (LiteLLM master key if proxied, else OpenRouter key)
API_KEY = os.getenv("LITELLM_API_KEY", OPENROUTER_API_KEY) if LITELLM_PROXY_URL else OPENROUTER_API_KEY

# Data directory for conversation storage
DATA_DIR = "data/conversations"
