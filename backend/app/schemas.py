# backend/app/schemas.py
from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    citations: List[str] = []

class UploadResponse(BaseModel):
    status: str
    message: str
    doc_id: str
    chunks_count: int