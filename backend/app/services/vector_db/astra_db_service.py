from typing import List, Dict, Tuple, Optional
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain_mistralai import MistralAIEmbeddings
import google.generativeai as genai

from app.config.settings import (
    ASTRA_DB_ID,
    ASTRA_DB_REGION,
    ASTRA_DB_APPLICATION_TOKEN,
    ASTRA_DB_KEYSPACE,
    GEMINI_API_KEY,
    MISTRAL_API_KEY,
    EMBEDDING_MODEL
)


class VectorDBService:
    """Service for managing vector database operations with Astra DB"""

    def __init__(self):
        """Initialize Astra DB connection and embeddings"""
        if not all([ASTRA_DB_ID, ASTRA_DB_APPLICATION_TOKEN, MISTRAL_API_KEY]):
            raise ValueError("Missing required environment variables for Astra DB or Mistral")
        
        # Configure Gemini for LLM only
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize embeddings using Mistral AI
        self.embeddings = MistralAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=MISTRAL_API_KEY
        )
        
        # Initialize Astra DB vector store
        self.vector_store = AstraDBVectorStore(
            collection_name="rag_documents",
            embedding=self.embeddings,
            api_endpoint=f"https://{ASTRA_DB_ID}-{ASTRA_DB_REGION}.apps.astra.datastax.com",
            token=ASTRA_DB_APPLICATION_TOKEN,
            namespace=ASTRA_DB_KEYSPACE
        )
        
        self.retriever = None

    def add_documents(self, documents: List[Document], document_id: str) -> int:
        """
        Add documents to the vector store
        
        Args:
            documents: List of Document objects to add
            document_id: ID of the document for tracking
            
        Returns:
            Number of documents added
        """
        try:
            # Add to vector store
            self.vector_store.add_documents(documents)
            return len(documents)
        except Exception as e:
            raise Exception(f"Failed to add documents to vector store: {str(e)}")

    def similarity_search(self, query: str, k: int = 3, document_id: Optional[str] = None) -> List[Tuple[Document, float]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            document_id: Optional filter by document ID
            
        Returns:
            List of (Document, similarity_score) tuples
        """
        try:
            if document_id:
                # Search with filter for specific document
                results = self.vector_store.similarity_search_with_score(
                    query,
                    k=k,
                    filter={"document_id": document_id}
                )
            else:
                # Search all documents
                results = self.vector_store.similarity_search_with_score(query, k=k)
            
            return results
        except Exception as e:
            raise Exception(f"Similarity search failed: {str(e)}")

    def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks of a document
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            # Delete from vector store by document_id metadata
            self.vector_store.delete(
                where={"document_id": {"$eq": document_id}}
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to delete document: {str(e)}")

    def get_retriever(self, k: int = 3):
        """
        Get a retriever for use in chains
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            LangChain retriever object
        """
        return self.vector_store.as_retriever(search_kwargs={"k": k})
