from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
import traceback

from app.models.schemas import DocumentUpload, DocumentResponse, QueryRequest, QueryResponse, RetrievedChunk
from app.services.document_processor import DocumentProcessor
from app.services.vector_db.astra_db_service import VectorDBService
from app.services.llm.gemini_service import LLMService

router = APIRouter(prefix="/api", tags=["rag"])

# Initialize services
doc_processor = DocumentProcessor()
vector_db_service = VectorDBService()
llm_service = LLMService()


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Query(None)
):
    """
    Upload a document for RAG processing
    
    Supported formats: PDF, TXT, MD
    """
    try:
        # Read file content
        content = await file.read()
        
        # Process the document
        document_id, documents = doc_processor.process_file(
            content,
            file.filename,
            metadata={"upload_filename": file.filename}
        )
        
        # Add to vector store
        chunks_added = vector_db_service.add_documents(documents, document_id)
        
        return DocumentResponse(
            document_id=document_id,
            filename=file.filename,
            chunks_created=chunks_added,
            message=f"Successfully processed document into {chunks_added} chunks"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing document: {str(e)}"
        )


@router.post("/documents/upload-text", response_model=DocumentResponse)
async def upload_text_document(request: DocumentUpload):
    """
    Upload text content directly for RAG processing
    """
    try:
        # Process the text
        document_id, documents = doc_processor.process_text(
            request.content,
            request.filename,
            metadata=request.metadata
        )
        
        # Add to vector store
        chunks_added = vector_db_service.add_documents(documents, document_id)
        
        return DocumentResponse(
            document_id=document_id,
            filename=request.filename,
            chunks_created=chunks_added,
            message=f"Successfully processed text into {chunks_added} chunks"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing text: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query documents for answers based on RAG
    """
    try:
        # Retrieve relevant documents
        results = vector_db_service.similarity_search(
            request.query,
            k=request.top_k,
            document_id=request.document_id
        )
        
        if not results:
            return QueryResponse(
                answer="No relevant information found to answer this question.",
                retrieved_chunks=[],
                document_id=request.document_id
            )
        
        # Extract documents and scores
        retrieved_docs = [doc for doc, score in results]
        scores = [score for doc, score in results]
        
        # Generate answer using LLM
        answer = llm_service.answer_question(request.query, retrieved_docs)
        
        # Prepare retrieved chunks for response
        retrieved_chunks = []
        for doc, score in results:
            chunk = RetrievedChunk(
                chunk_text=doc.page_content,
                metadata=doc.metadata,
                similarity_score=float(score)
            )
            retrieved_chunks.append(chunk)
        
        return QueryResponse(
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            document_id=request.document_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing query: {str(e)}"
        )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks from the vector store
    """
    try:
        success = vector_db_service.delete_document(document_id)
        
        return {
            "success": success,
            "message": f"Document {document_id} deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error deleting document: {str(e)}"
        )
