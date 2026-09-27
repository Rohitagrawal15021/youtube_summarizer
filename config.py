import os
import time
import random
from dotenv import load_dotenv
from google import genai
from google.genai import errors

# Load .env file
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# HTTP status codes that are transient and worth retrying.
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}

# ---- Groq fallback ----------------------------------------------------------

_groq_client = None


def _get_groq_client():
    """Lazily build the Groq client. Returns None if key/SDK is unavailable."""
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        try:
            from groq import Groq
        except ModuleNotFoundError:
            return None
        _groq_client = Groq(api_key=api_key)
    return _groq_client


class _GroqResponse:
    """Minimal stand-in exposing `.text`, so Gemini callers work unchanged."""

    def __init__(self, text):
        self.text = text


def _groq_fallback(model=None, contents=None, config=None, **_ignored):
    """Answer the same prompt with Groq. Returns a response-like obj or None."""
    groq = _get_groq_client()
    if groq is None:
        return None

    prompt = contents if isinstance(contents, str) else str(contents)
    temperature = getattr(config, "temperature", None)
    max_tokens = getattr(config, "max_output_tokens", None)
    want_json = getattr(config, "response_mime_type", None) == "application/json"

    messages = []
    if want_json:
        messages.append({
            "role": "system",
            "content": "You must respond with valid JSON only. No prose, no markdown.",
        })
    messages.append({"role": "user", "content": prompt})

    call = {
        "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        "messages": messages,
        "temperature": 0 if temperature is None else temperature,
    }
    if max_tokens:
        call["max_completion_tokens"] = max_tokens
    if want_json:
        call["response_format"] = {"type": "json_object"}

    try:
        completion = groq.chat.completions.create(**call)
        print(f"Gemini unavailable — fell back to Groq ({call['model']}).")
        return _GroqResponse(completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq fallback also failed: {e}")
        return None


def generate_with_retry(max_retries=2, base_delay=1.0, max_delay=8.0, **kwargs):
    """
    Wrapper around client.models.generate_content that retries on transient
    errors (e.g. 503 UNAVAILABLE "high demand") using exponential backoff with
    jitter, then falls back to Groq if Gemini is still unavailable.

    Defaults are kept deliberately short (2 quick retries, ~3s total) because
    we have a capable Groq fallback: when Gemini is broadly overloaded it's far
    better to fail over to Groq in a few seconds than to sleep ~60s per call.
    A real run makes many LLM calls, so slow per-call backoff stacks into
    multi-minute hangs behind the synchronous /process request.

    Pass the same arguments you would pass to client.models.generate_content,
    e.g. model=..., contents=..., config=...

    Raises the last Gemini error if retries are exhausted and Groq is not
    configured / also fails.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return client.models.generate_content(**kwargs)
        except errors.APIError as e:
            last_error = e
            status = getattr(e, "code", None)
            # Non-retryable error, or last attempt used: stop hitting Gemini.
            if status not in _RETRYABLE_STATUS or attempt == max_retries:
                break
            delay = min(base_delay * (2 ** attempt), max_delay)
            delay += random.uniform(0, delay * 0.25)
            print(
                f"Gemini returned {status}. Retry {attempt + 1}/{max_retries} "
                f"in {delay:.1f}s..."
            )
            time.sleep(delay)

    # Gemini exhausted — try Groq before giving up.
    fallback = _groq_fallback(**kwargs)
    if fallback is not None:
        return fallback

    raise last_error