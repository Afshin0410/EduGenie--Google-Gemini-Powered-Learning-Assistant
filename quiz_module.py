import json
import re

from gemini_client import ask_gemini

_QUIZ_PROMPT = """Create exactly 3 multiple-choice questions from the following source.
The source may be a full passage or a short topic.

Each item must have:
- "question": a string
- "options": a list of exactly 4 distinct answer strings
- "answer": a string that exactly matches one of the options (same text, not A/B/C/D)

Return JSON only. No markdown, no code fences, no extra text.
Use this shape:
[
  {{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}},
  {{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}},
  {{"question": "...", "options": ["...", "...", "...", "..."], "answer": "..."}}
]

Source:
{source}
"""

_RETRY_PROMPT = """Your previous response was not valid JSON in the required quiz format.
Return JSON only (no markdown) with exactly 3 items. Each item must have "question",
"options" (exactly 4 strings), and "answer" that exactly matches one option.

Source:
{source}
"""


def _strip_markdown_fences(raw: str) -> str:
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_items(data) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("quiz", "questions", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    raise ValueError("JSON must be a list of quiz items.")


def _validate_quiz(items: list) -> list[dict]:
    if len(items) != 3:
        raise ValueError("Quiz must contain exactly 3 questions.")

    validated: list[dict] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Question {index} is not an object.")

        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")

        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Question {index} is missing a valid 'question'.")
        if not isinstance(options, list) or len(options) != 4:
            raise ValueError(f"Question {index} must have exactly 4 options.")
        if not all(isinstance(option, str) and option.strip() for option in options):
            raise ValueError(f"Question {index} has an invalid option.")
        if not isinstance(answer, str) or answer not in options:
            raise ValueError(
                f"Question {index} answer must exactly match one of the options."
            )

        stripped_options = [option.strip() for option in options]
        validated.append(
            {
                "question": question.strip(),
                "options": stripped_options,
                "answer": stripped_options[options.index(answer)],
            }
        )
    return validated


def _try_parse_quiz(raw: str) -> list[dict]:
    if raw.startswith("Error"):
        raise ValueError(raw)
    cleaned = _strip_markdown_fences(raw)
    data = json.loads(cleaned)
    return _validate_quiz(_extract_items(data))


def generate_quiz(text_or_topic: str):
    """Generate 3 validated MCQs from a passage or short topic."""
    last_error = "Could not generate a valid quiz."

    for attempt, template in enumerate((_QUIZ_PROMPT, _RETRY_PROMPT), start=1):
        raw = ask_gemini(template.format(source=text_or_topic.strip()))
        try:
            return _try_parse_quiz(raw)
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            last_error = str(exc)
            if attempt == 1:
                continue

    return f"Error generating quiz: {last_error}"
