from gemini_client import ask_gemini


def explain_topic(topic: str) -> str:
    prompt = (
        f"Explain '{topic}' in a simple and clear way for a school student, "
        "under 150 words, with one everyday analogy."
    )
    return ask_gemini(prompt)
