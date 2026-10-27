"""Unified AI service wrapper leveraging the official Google Gen AI SDK."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


class AIServiceError(Exception):
    """Base exception for AI service operations."""


class APIKeyMissingError(AIServiceError):
    """Raised when an API key is required but not provided or configured."""


class AIProviderUnavailableError(AIServiceError):
    """Raised when google-genai SDK is not installed or service cannot be reached."""


class AIResponseFormatError(AIServiceError):
    """Raised when AI response is not valid JSON or violates schema."""


class APIAuthError(AIServiceError):
    """Raised when Gemini returns authentication or permission errors."""


class APIRateLimitError(AIServiceError):
    """Raised when Gemini quota or rate limits are reached."""


def is_genai_installed() -> bool:
    """Return True if the official google-genai library is installed."""
    return GENAI_AVAILABLE


def resolve_api_key(session_api_key: Optional[str] = None) -> Optional[str]:
    """Resolve Gemini API key with strict precedence:
    1. Session-level user input (for local interactive testing)
    2. Streamlit secrets (if running inside Streamlit)
    3. Environment variable GEMINI_API_KEY
    """
    if session_api_key and session_api_key.strip():
        return session_api_key.strip()

    # Attempt to read from streamlit secrets if available
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
            if key and str(key).strip():
                return str(key).strip()
    except Exception:
        pass

    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    return None


def resolve_model_name(session_model: Optional[str] = None) -> str:
    """Resolve model name from session, secrets, environment or fallback default."""
    if session_model and session_model.strip():
        return session_model.strip()

    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_MODEL" in st.secrets:
            model = st.secrets["GEMINI_MODEL"]
            if model and str(model).strip():
                return str(model).strip()
    except Exception:
        pass

    env_model = os.environ.get("GEMINI_MODEL")
    if env_model and env_model.strip():
        return env_model.strip()

    return DEFAULT_GEMINI_MODEL


def get_genai_client(api_key: Optional[str]):
    """Initialize and return a google-genai Client."""
    if not is_genai_installed():
        raise AIProviderUnavailableError(
            "The 'google-genai' SDK is not installed in the current Python environment. "
            "Please run: pip install google-genai"
        )

    resolved_key = resolve_api_key(api_key)
    if not resolved_key:
        raise APIKeyMissingError(
            "No Google Gemini API key detected. Please configure GEMINI_API_KEY in environment, "
            ".streamlit/secrets.toml, or enter it in the dashboard sidebar."
        )

    try:
        client = genai.Client(api_key=resolved_key)
        return client
    except Exception as exc:
        raise AIServiceError(f"Failed to initialize Gemini Client: {str(exc)}") from exc


def extract_json_from_text(raw_text: str) -> Dict[str, Any]:
    """Safely extract and parse JSON from raw text or markdown code blocks."""
    if not raw_text or not raw_text.strip():
        raise AIResponseFormatError("Received empty response from AI model.")

    cleaned = raw_text.strip()

    # Remove markdown code block if present
    if "```json" in cleaned:
        pattern = r"```json\s*(.*?)\s*```"
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
    elif "```" in cleaned:
        pattern = r"```\s*(.*?)\s*```"
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()

    # Attempt direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: find enclosing outermost { and }
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            sliced = cleaned[start_idx : end_idx + 1]
            try:
                return json.loads(sliced)
            except json.JSONDecodeError as inner_exc:
                raise AIResponseFormatError(
                    f"AI generated text was not valid JSON: {str(inner_exc)}\nRaw: {cleaned[:300]}"
                ) from inner_exc

        raise AIResponseFormatError(
            f"Failed to find valid JSON structure in AI response. Text: {cleaned[:300]}"
        )


def analyze_image_with_gemini(
    api_key: Optional[str],
    model: str,
    prompt: str,
    image_bytes: bytes,
    mime_type: str,
    system_instruction: Optional[str] = None,
) -> Dict[str, Any]:
    """Submit image and prompt to Gemini vision model and parse structured JSON."""
    client = get_genai_client(api_key)

    try:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        )

        config_params: Dict[str, Any] = {
            "response_mime_type": "application/json",
            "temperature": 0.2,  # Low temperature for factual, safety-oriented consistency
        }
        if system_instruction:
            config_params["system_instruction"] = system_instruction

        config = types.GenerateContentConfig(**config_params)

        response = client.models.generate_content(
            model=model,
            contents=[image_part, prompt],
            config=config,
        )

        if not response or not response.text:
            raise AIResponseFormatError("Gemini returned an empty response.")

        return extract_json_from_text(response.text)

    except (APIKeyMissingError, AIProviderUnavailableError, AIResponseFormatError):
        raise
    except Exception as exc:
        err_msg = str(exc).lower()
        if "403" in err_msg or "401" in err_msg or "api_key" in err_msg or "permission" in err_msg:
            raise APIAuthError(f"Authentication failure with Gemini API: {str(exc)}") from exc
        if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
            raise APIRateLimitError(f"Gemini API rate limit or quota exceeded: {str(exc)}") from exc
        raise AIServiceError(f"Gemini Vision call failed: {str(exc)}") from exc


def ask_site_assistant_gemini(
    api_key: Optional[str],
    model: str,
    question: str,
    weather_context: Optional[str] = None,
) -> str:
    """Generate professional, contextual response to construction engineering questions."""
    client = get_genai_client(api_key)

    system_instruction = (
        "You are a master civil engineer and certified site safety officer (PE / CSP). "
        "Provide direct, actionable, practical, and standards-compliant construction guidance. "
        "Identify implicit assumptions, cite standard engineering checks (e.g., slump test, formwork check, rebar inspection, PTW), "
        "and always advise verification with the project's engineer of record (EOR) for critical decisions. "
        "Keep answers concise, structured with bullet points, and free of unnecessary fluff."
    )

    full_prompt = f"Question: {question.strip()}\n"
    if weather_context:
        full_prompt += f"Current Weather & Site Advisory Context: {weather_context}\n"

    try:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
        )
        response = client.models.generate_content(
            model=model,
            contents=[full_prompt],
            config=config,
        )
        if not response or not response.text:
            return "No response received from the assistant. Please try rephrasing your inquiry."
        return response.text.strip()
    except Exception as exc:
        err_msg = str(exc).lower()
        if "403" in err_msg or "401" in err_msg or "api_key" in err_msg:
            raise APIAuthError(f"Authentication failure: {str(exc)}") from exc
        if "429" in err_msg or "quota" in err_msg:
            raise APIRateLimitError(f"Rate limit exceeded: {str(exc)}") from exc
        raise AIServiceError(f"Site Assistant request failed: {str(exc)}") from exc
