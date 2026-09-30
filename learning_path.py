from gemini_client import ask_gemini


def get_learning_recommendations(topic: str) -> str:
    prompt = (
        "Act as an AI tutor. Give a structured learning path for this topic "
        "with beginner, intermediate, and advanced levels. For each level include "
        "estimated time, key topics, and resources.\n\n"
        f"Topic: {topic}"
    )
    return ask_gemini(prompt)
