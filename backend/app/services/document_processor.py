import os
from typing import List, Dict, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import PyPDF2
from io import BytesIO
import uuid

from app.config.settings import CHUNK_SIZE, CHUNK_OVERLAP


class DocumentProcessor:
    """Handles document processing, parsing, and chunking"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_text(self, text: str, filename: str, metadata: Dict = None) -> Tuple[str, List[Document]]:
        """
        Process text content and create chunks
        
        Args:
            text: Text content to process
            filename: Source filename for metadata
            metadata: Additional metadata to attach
            
        Returns:
            Tuple of (document_id, list of Document chunks)
        """
        document_id = str(uuid.uuid4())
        
        # Create base metadata
        base_metadata = {
            "document_id": document_id,
            "filename": filename,
            "source": filename,
        }
        
        if metadata:
            base_metadata.update(metadata)
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create Document objects with metadata
        documents = []
        for idx, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = idx
            chunk_metadata["total_chunks"] = len(chunks)
            
            doc = Document(
                page_content=chunk,
                metadata=chunk_metadata
            )
            documents.append(doc)
        
        return document_id, documents

    def process_pdf(self, file_content: bytes, filename: str, metadata: Dict = None) -> Tuple[str, List[Document]]:
        """
        Extract text from PDF and create chunks
        
        Args:
            file_content: PDF file bytes
            filename: Source filename for metadata
            metadata: Additional metadata to attach
            
        Returns:
            Tuple of (document_id, list of Document chunks)
        """
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
            
            # Process the extracted text
            return self.process_text(text, filename, metadata)
        
        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")

    def process_file(self, file_content: bytes, filename: str, metadata: Dict = None) -> Tuple[str, List[Document]]:
        """
        Process file based on extension
        
        Args:
            file_content: File bytes
            filename: Filename with extension
            metadata: Additional metadata to attach
            
        Returns:
            Tuple of (document_id, list of Document chunks)
        """
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext == ".pdf":
            return self.process_pdf(file_content, filename, metadata)
        elif file_ext in [".txt", ".md"]:
            text = file_content.decode('utf-8')
            return self.process_text(text, filename, metadata)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
