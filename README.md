# EduGenie

EduGenie is a FastAPI study companion that uses Google Gemini to answer questions, explain topics, summarize notes, generate quizzes, and suggest learning paths. A single-page UI lets students pick a task, submit text, and read the result.

## Live Demo

🔗 **Live App:** [https://edugenie-x2r7.onrender.com](https://edugenie-x2r7.onrender.com)

> **Note:** The free tier instance may take up to a minute to wake up on the first request.

## Features

- Q&A for student questions
- Simple explanations with an everyday analogy
- Summaries in plain language
- 3-question multiple-choice quizzes with in-page answer checking
- Structured learning paths (beginner / intermediate / advanced)
- Gemini retries with backoff on 429/503 responses
- Input validation (required fields, 5000-character limit)

## Tech stack

- Python 3
- FastAPI and Uvicorn
- Jinja2 templates and static CSS
- `google-genai` SDK (`from google import genai`)
- python-dotenv for environment variables

## Folder structure

```
EduGenie/
  main.py                 # FastAPI app and API routes
  gemini_client.py        # Gemini client and ask_gemini helper
  explanation_module.py
  qna.py
  quiz_module.py
  summary_module.py
  learning_path.py
  templates/
    index.html            # Single-page UI
  static/
    style.css
  requirements.txt
  .env.example            # Placeholder env vars (copy to .env)
  .gitignore
  README.md
```

## Setup

1. Create and activate a virtual environment.

   Windows (PowerShell):

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   macOS / Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the example (do not commit `.env`):

   ```bash
   copy .env.example .env
   ```

   On macOS / Linux:

   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and set your real values:

   - `GEMINI_API_KEY` — your Gemini API key
   - `GEMINI_MODEL` — model name, for example `gemini-3.6-flash`

   Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

## Run

From the project root, with the virtual environment activated:

```bash
uvicorn main:app --reload --port 8080
```

Then open [http://127.0.0.1:8080](http://127.0.0.1:8080).

## API endpoints

| Method | Path | JSON body | Success response |
| --- | --- | --- | --- |
| GET | `/` | — | HTML UI |
| POST | `/qa` | `{ "question": "..." }` | `{ "answer": "..." }` |
| POST | `/explain` | `{ "topic": "..." }` | `{ "topic": "...", "explanation": "..." }` |
| POST | `/summarize` | `{ "text": "..." }` | `{ "summary": "..." }` |
| POST | `/quiz` | `{ "text": "..." }` | `{ "quiz": [ { "question", "options", "answer" } ] }` |
| POST | `/learn/recommendations` | `{ "topic": "..." }` | `{ "recommendation": "..." }` |

Empty or whitespace-only fields, and inputs longer than 5000 characters, return **400**. Unexpected server errors return **500**.
