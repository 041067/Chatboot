from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.response_service import ResponseService
from app.core.metrics import get_metrics_history


def create_router(service: ResponseService) -> APIRouter:
    router = APIRouter()

    class ChatRequest(BaseModel):
        message: str

    @router.post("/chat")
    @router.post("/api/chat")
    async def chat(request: ChatRequest):
        try:
            result = service.process(request.message)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/health")
    @router.get("/api/health")
    async def health():
        return {
            "status": "ok",
            "pdf_loaded": bool(service.pdf_chunks),
            "chunks": len(service.pdf_chunks) if service.pdf_chunks else 0,
        }

    @router.post("/reset")
    async def reset():
        service.reset_memory()
        return {"status": "memoria reiniciada"}

    @router.get("/metrics")
    async def metrics():
        return {"metrics": get_metrics_history()}

    return router
