"""
Example script demonstrating how to use the RAG API
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def health_check():
    """Check if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"API Health: {response.json()}")
    except Exception as e:
        print(f"API is not running: {e}")
        return False
    return True


def upload_text_document(filename: str, content: str):
    """Upload text content to the RAG system"""
    payload = {
        "filename": filename,
        "content": content,
        "metadata": {
            "source": "example",
            "type": "text"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/documents/upload-text", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Document uploaded successfully!")
        print(f"  Document ID: {result['document_id']}")
        print(f"  Chunks created: {result['chunks_created']}")
        return result['document_id']
    else:
        print(f"Upload failed: {response.json()}")
        return None


def upload_file_document(file_path: str):
    """Upload a file to the RAG system"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return None
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Document uploaded successfully!")
        print(f"  Document ID: {result['document_id']}")
        print(f"  Chunks created: {result['chunks_created']}")
        return result['document_id']
    else:
        print(f"Upload failed: {response.json()}")
        return None


def query_document(query: str, document_id: str = None, top_k: int = 3):
    """Query the RAG system"""
    payload = {
        "query": query,
        "top_k": top_k
    }
    
    if document_id:
        payload["document_id"] = document_id
    
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📚 Query: {query}")
        print(f"💡 Answer: {result['answer']}")
        print(f"\n📖 Source chunks ({len(result['retrieved_chunks'])} found):")
        for i, chunk in enumerate(result['retrieved_chunks'], 1):
            print(f"\n  [{i}] Similarity: {chunk['similarity_score']:.2%}")
            print(f"      {chunk['chunk_text'][:150]}...")
    else:
        print(f"✗ Query failed: {response.json()}")


def delete_document(document_id: str):
    """Delete a document from the RAG system"""
    response = requests.delete(f"{BASE_URL}/api/documents/{document_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"{result['message']}")
    else:
        print(f"Delete failed: {response.json()}")


def main():
    """Main example flow"""
    print("=" * 60)
    print("Knowledge Based RAG API - Example Usage")
    print("=" * 60)
    
    # Check if API is running
    if not health_check():
        print("\nPlease start the API server first:")
        print("  python -m uvicorn app.main:app --reload")
        return
    
    print("\n" + "=" * 60)
    print("Step 1: Upload a Document")
    print("=" * 60)
    
    # Example content
    sample_content = """
    Artificial Intelligence (AI) is the simulation of human intelligence processes by computer systems.
    These processes include learning, reasoning, and self-correction.
    
    AI applications include expert systems, natural language processing, and robotics.
    Machine learning, a subset of AI, enables systems to learn from data without being explicitly programmed.
    
    Deep learning uses neural networks with multiple layers to process complex patterns.
    Common applications include image recognition, language translation, and autonomous vehicles.
    
    AI is transforming industries like healthcare, finance, and transportation.
    However, ethical considerations such as bias and privacy are important concerns.
    """
    
    document_id = upload_text_document("ai_overview.txt", sample_content)
    
    if not document_id:
        print("Failed to upload document")
        return
    
    print("\n" + "=" * 60)
    print("Step 2: Query the Document")
    print("=" * 60)
    
    # Example queries
    queries = [
        "What is artificial intelligence?",
        "Name some applications of AI",
        "What are concerns about AI?"
    ]
    
    for query in queries:
        query_document(query, document_id, top_k=3)
        print("\n" + "-" * 60)
    
    print("\n" + "=" * 60)
    print("Step 3: Query All Documents (without specific document_id)")
    print("=" * 60)
    
    query_document("What is deep learning?")
    
    print("\n" + "=" * 60)
    print("Example Complete!")
    print("=" * 60)
    print(f"\nDocument ID for manual testing: {document_id}")
    print(f"To delete this document later, use: delete_document('{document_id}')")


if __name__ == "__main__":
    main()
