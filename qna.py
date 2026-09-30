from gemini_client import ask_gemini


def answer_question(question: str) -> str:
    prompt = (
        "Answer the following question clearly and accurately for a student.\n\n"
        f"Question: {question}"
    )
    return ask_gemini(prompt)
