from gemini_client import ask_gemini


def summarize_text(text: str) -> str:
    prompt = (
        "Summarize the following text in simple language. "
        "Keep the main ideas and make it easy to understand.\n\n"
        f"{text}"
    )
    return ask_gemini(prompt)
