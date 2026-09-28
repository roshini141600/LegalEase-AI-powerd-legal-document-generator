from fastapi import APIRouter, HTTPException

from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.schemas import DocumentRequest, DocumentResponse

router = APIRouter()
generator = GeminiDocumentGenerator()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "ai_configured": generator.configured,
    }


@router.post("/generate", response_model=DocumentResponse)
def generate_legal_document(request: DocumentRequest):
    try:
        document, model = generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )
        return DocumentResponse(
            document=document,
            model=model,
            source="gemini" if model != "demo" else "demo",
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
