import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger("edugenie.gemini")

client = genai.Client()

_BUSY_MESSAGE = (
    "The AI service is busy right now, please try again in a moment."
)
_RETRY_DELAYS = (1, 2, 4)


def _is_busy_error(exc: Exception) -> bool:
    code = getattr(exc, "code", None)
    if code in (429, 503):
        return True
    text = str(exc)
    return "429" in text or "503" in text


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the model text, or a clear error."""
    try:
        model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash") or "gemini-3.6-flash"

        last_error: Exception | None = None
        for attempt in range(len(_RETRY_DELAYS) + 1):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                text = response.text
                if not text:
                    logger.warning("Gemini returned an empty response")
                    return "Error: Gemini returned an empty response."
                return text.strip()
            except Exception as exc:
                last_error = exc
                if _is_busy_error(exc) and attempt < len(_RETRY_DELAYS):
                    delay = _RETRY_DELAYS[attempt]
                    logger.warning(
                        "Gemini busy (attempt %s), retrying in %ss: %s",
                        attempt + 1,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
                    continue
                if _is_busy_error(exc):
                    logger.error("Gemini still busy after retries")
                    return _BUSY_MESSAGE
                logger.exception("Gemini request failed")
                return f"Error calling Gemini: {exc}"

        if last_error is not None and _is_busy_error(last_error):
            return _BUSY_MESSAGE
        return f"Error calling Gemini: {last_error}"
    except Exception as exc:
        logger.exception("Unexpected Gemini client error")
        return f"Error calling Gemini: {exc}"
