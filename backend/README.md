# Knowledge Based RAG API

A simple Retrieval-Augmented Generation (RAG) system that processes documents using chunking and embeddings, stores them in Astra DB, and uses Google Gemini LLM to answer questions based on the document content.

## Features

- **Document Processing**: Upload PDF, TXT, or MD files
- **Intelligent Chunking**: Automatic text chunking with configurable size and overlap
- **Vector Storage**: Astra DB vector database for efficient retrieval
- **Mistral AI Embeddings**: High-quality embeddings using Mistral AI
- **Smart Retrieval**: Semantic similarity search to find relevant document chunks
- **LLM Integration**: Google Gemini for high-quality answer generation
- **RESTful API**: FastAPI-based endpoints for all operations

## Architecture

```
Document Upload
    ↓
Document Processor (Chunking)
    ↓
Google Embeddings
    ↓
Astra DB Vector Store
    ↓
Similarity Search → Retrieved Chunks → Gemini LLM → Answer
```

## Prerequisites

- Python 3.8+
- Astra DB account and credentials
- Google Gemini API key

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# Astra DB Configuration
# Option A: direct endpoint connection (preferred when you have the endpoint)
ASTRA_DB_API_ENDPOINT=https://your_db_endpoint
ASTRA_DB_APPLICATION_TOKEN=your_token
ASTRA_DB_KEYSPACE=default_keyspace

# Option B: legacy ID/region form
ASTRA_DB_ID=your_astra_db_id
ASTRA_DB_REGION=your_region
ASTRA_DB_APPLICATION_TOKEN=your_token
ASTRA_DB_KEYSPACE=default_keyspace

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-pro

# Mistral AI Configuration
MISTRAL_API_KEY=your_mistral_api_key
EMBEDDING_MODEL=mistral-embed

# RAG Configuration (Optional - defaults provided)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 3. Get Your Credentials

#### Astra DB:
1. Go to [Astra DB](https://astra.datastax.com)
2. Create a new database
3. Generate an application token
4. Copy the Database ID and Region

#### Google Gemini:
1. Go to [Google AI Studio](https://ai.google.dev)
2. Create an API key
3. Copy the API key

#### Mistral AI:
1. Go to [Mistral AI Console](https://console.mistral.ai)
2. Create an API key
3. Copy the API key

## Running the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Health Check
```bash
GET /health
```

### 2. Upload Document (File)
```bash
POST /api/documents/upload
Content-Type: multipart/form-data

- file: [PDF/TXT/MD file]
- metadata (optional): JSON string with additional metadata
```

Response:
```json
{
  "document_id": "uuid",
  "filename": "document.pdf",
  "chunks_created": 42,
  "message": "Successfully processed document into 42 chunks"
}
```

### 3. Upload Text Document
```bash
POST /api/documents/upload-text
Content-Type: application/json

{
  "filename": "my_document.txt",
  "content": "Document content here...",
  "metadata": {
    "source": "email",
    "date": "2024-01-01"
  }
}
```

### 4. Query Documents
```bash
POST /api/query
Content-Type: application/json

{
  "query": "What is the main topic?",
  "document_id": "optional_uuid",
  "top_k": 3
}
```

Response:
```json
{
  "answer": "The main topic is...",
  "retrieved_chunks": [
    {
      "chunk_text": "...",
      "metadata": {...},
      "similarity_score": 0.92
    }
  ],
  "document_id": "optional_uuid"
}
```

### 5. Delete Document
```bash
DELETE /api/documents/{document_id}
```

## Example Usage

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Upload a document
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
    document_id = response.json()["document_id"]

# Query the document
query_data = {
    "query": "What is this document about?",
    "document_id": document_id,
    "top_k": 3
}
response = requests.post(f"{BASE_URL}/api/query", json=query_data)
result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['retrieved_chunks'])} chunks retrieved")
```

### Using cURL

```bash
# Upload document
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf"

# Query
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "top_k": 3
  }'
```

## Configuration

Edit `app/config/settings.py` to modify:

- `CHUNK_SIZE`: Size of text chunks (default: 1000 tokens)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 tokens)
- `GEMINI_MODEL`: Gemini model to use (default: gemini-1.5-pro)

## Project Structure

```
backend/
├── app/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── services/
│   │   ├── document_processor.py # Document parsing & chunking
│   │   ├── llm/
│   │   │   └── gemini_service.py # Gemini LLM service
│   │   └── vector_db/
│   │       └── astra_db_service.py # Astra DB operations
│   ├── routes/
│   │   └── rag_routes.py        # API endpoints
│   └── main.py                  # FastAPI app entry point
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variables template
```

## How It Works

1. **Document Upload**: User uploads a document (PDF, TXT, MD)
2. **Processing**: Document is split into overlapping chunks
3. **Embedding**: Each chunk is embedded using Google's embedding model
4. **Storage**: Embeddings and chunks are stored in Astra DB
5. **Query**: User asks a question
6. **Retrieval**: System finds most relevant chunks using semantic search
7. **Generation**: Gemini LLM generates answer based on retrieved chunks
8. **Response**: Answer and source chunks are returned to user

## Troubleshooting

### Missing Environment Variables
Ensure all required variables are set in `.env` file and the file is in the backend directory.

### Connection Issues
- Verify Astra DB credentials are correct
- Check internet connection for Gemini API
- Ensure tokens haven't expired

### No Results Found
- Check if documents are properly uploaded
- Verify the query is related to document content
- Try adjusting `top_k` parameter

## Future Enhancements

- Multi-language support
- Document filtering by date/source
- Batch processing
- Authentication & authorization
- Rate limiting
- Caching layer
- Support for more document formats

