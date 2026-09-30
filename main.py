import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("edugenie")

MAX_INPUT_LENGTH = 5000

app = FastAPI(title="EduGenie")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class QARequest(BaseModel):
    question: str


class SummarizeRequest(BaseModel):
    text: str


class LearnRequest(BaseModel):
    topic: str


class QuizRequest(BaseModel):
    text: str


class ExplainRequest(BaseModel):
    topic: str


def require_field(value: str, field_name: str) -> str:
    if value is None or not str(value).strip():
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} cannot be empty.",
        )
    cleaned = str(value).strip()
    if len(cleaned) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"{field_name} must be at most {MAX_INPUT_LENGTH} characters."
            ),
        )
    return cleaned


@app.get("/")
async def home(request: Request):
    try:
        logger.info("GET /")
        return templates.TemplateResponse(request=request, name="index.html")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to render home page")
        raise HTTPException(
            status_code=500,
            detail="Could not load the page. Please try again.",
        )


@app.post("/qa")
async def qa(payload: QARequest):
    try:
        question = require_field(payload.question, "question")
        logger.info("POST /qa")
        return {"answer": answer_question(question)}
    except HTTPException:
        raise
    except Exception:
        logger.exception("POST /qa failed")
        raise HTTPException(
            status_code=500,
            detail="Could not generate an answer. Please try again.",
        )


@app.post("/summarize")
async def summarize(payload: SummarizeRequest):
    try:
        text = require_field(payload.text, "text")
        logger.info("POST /summarize")
        return {"summary": summarize_text(text)}
    except HTTPException:
        raise
    except Exception:
        logger.exception("POST /summarize failed")
        raise HTTPException(
            status_code=500,
            detail="Could not generate a summary. Please try again.",
        )


@app.post("/learn/recommendations")
async def learn_recommendations(payload: LearnRequest):
    try:
        topic = require_field(payload.topic, "topic")
        logger.info("POST /learn/recommendations")
        return {"recommendation": get_learning_recommendations(topic)}
    except HTTPException:
        raise
    except Exception:
        logger.exception("POST /learn/recommendations failed")
        raise HTTPException(
            status_code=500,
            detail="Could not generate learning recommendations. Please try again.",
        )


@app.post("/quiz")
async def quiz(payload: QuizRequest):
    try:
        text = require_field(payload.text, "text")
        logger.info("POST /quiz")
        result = generate_quiz(text)
        if isinstance(result, str):
            logger.error("Quiz generation failed: %s", result)
            raise HTTPException(status_code=500, detail=result)
        return {"quiz": result}
    except HTTPException:
        raise
    except Exception:
        logger.exception("POST /quiz failed")
        raise HTTPException(
            status_code=500,
            detail="Could not generate a quiz. Please try again.",
        )


@app.post("/explain")
async def explain(payload: ExplainRequest):
    try:
        topic = require_field(payload.topic, "topic")
        logger.info("POST /explain")
        return {"topic": topic, "explanation": explain_topic(topic)}
    except HTTPException:
        raise
    except Exception:
        logger.exception("POST /explain failed")
        raise HTTPException(
            status_code=500,
            detail="Could not generate an explanation. Please try again.",
        )
