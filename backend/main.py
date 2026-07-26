import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

from search_engine import load_pdf_chunks, search_pdf
from question_analyzer import analyze_user_question, get_intent_group_label
from context_builder import build_context, build_contextual_prompt
from prompt_builder import PromptBuilder
from post_processor import post_process
from utils import summarize_response

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

app = FastAPI(title="Chatbot RAG Vida Loka - SENAI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("ERRO: A chave GROQ_API_KEY nao foi encontrada no arquivo .env!")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    async def index():
        return FileResponse(STATIC_DIR / "index.html")


class ChatRequest(BaseModel):
    message: str


PDF_PATH = BASE_DIR / "assets" / "documents" / "PlanoCursoDS.pdf"
pdf_chunks = load_pdf_chunks(PDF_PATH)
conversation_history: list[dict] = []
MAX_HISTORY = 5

NO_CONTEXT_MSG = (
    "Desculpe, mas nao encontrei essa informacao especifica no Plano de Curso atual. "
    "Posso responder perguntas sobre objetivos, requisitos, carga horaria, unidades curriculares, "
    "perfil profissional, mercado de trabalho, estagio e certificacao do curso."
)


def call_groq(system_prompt: str, user_prompt: str) -> str:
    if client is None:
        raise RuntimeError("GROQ_API_KEY nao configurada. Verifique o arquivo backend/.env.")
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content


@app.post("/api/chat")
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_message = request.message

        question_analysis = analyze_user_question(user_message)
        intent = question_analysis["intent"]
        depth = question_analysis["expected_depth"]
        style = question_analysis["answer_style"]

        paginas_encontradas = search_pdf(user_message, intent, pdf_chunks)

        context = build_context(paginas_encontradas)
        if not context.strip():
            return {
                "response": NO_CONTEXT_MSG,
                "sources": [],
                "analysis": question_analysis,
            }

        history = build_contextual_prompt(conversation_history, MAX_HISTORY)
        intent_label = get_intent_group_label(intent)

        system_prompt, user_prompt = PromptBuilder(
            question=user_message,
            context=context,
            intent_label=intent_label,
            depth=depth,
            style=style,
            history=history,
        )

        resposta = call_groq(system_prompt, user_prompt)
        resposta = post_process(resposta)

        conversation_history.append({
            "timestamp": str(len(conversation_history) + 1),
            "user_message": user_message,
            "intent": intent,
            "analysis": question_analysis,
            "response_summary": summarize_response(resposta),
        })

        if len(conversation_history) > MAX_HISTORY:
            conversation_history.pop(0)

        return {
            "response": resposta,
            "sources": [
                {"page": page_num, "score": round(score, 2)}
                for _, page_num, score, _ in paginas_encontradas[:5]
            ],
            "analysis": question_analysis,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "pdf_loaded": bool(pdf_chunks),
        "chunks": len(pdf_chunks),
        "pdf": PDF_PATH.name,
    }


if __name__ == "__main__":
    import uvicorn
    print("API rodando em http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
