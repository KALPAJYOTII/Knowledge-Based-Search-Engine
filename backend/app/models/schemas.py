from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentUpload(BaseModel):
    """Model for document upload request"""
    filename: str = Field(..., description="Name of the document")
    content: str = Field(..., description="Text content of the document")
    metadata: Optional[dict] = Field(default_factory=dict, description="Optional metadata")


class DocumentResponse(BaseModel):
    """Model for successful document upload response"""
    document_id: str
    filename: str
    chunks_created: int
    message: str


class QueryRequest(BaseModel):
    """Model for query request"""
    query: str = Field(..., description="User's question")
    document_id: Optional[str] = Field(None, description="Optional specific document ID to search")
    top_k: int = Field(default=3, description="Number of relevant chunks to retrieve")


class RetrievedChunk(BaseModel):
    """Model for a retrieved document chunk"""
    chunk_text: str
    metadata: dict
    similarity_score: Optional[float] = None


class QueryResponse(BaseModel):
    """Model for query response with answer and sources"""
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    document_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Model for health check response"""
    status: str
    message: str
