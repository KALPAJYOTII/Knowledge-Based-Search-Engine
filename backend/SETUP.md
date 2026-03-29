# RAG System Setup Guide

This guide will help you set up and run the Knowledge Based RAG system.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection (for API calls)

## Step 1: Get API Credentials

### Google Gemini API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Click "Get API Key"
3. Create a new API key
4. Copy and save the key

### Mistral AI API Key

1. Go to [Mistral AI Console](https://console.mistral.ai/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and save the key

### Astra DB Credentials

1. Visit [Astra DB](https://astra.datastax.com/)
2. Sign up or log in
3. Create a new database:
   - Choose any name
   - Select a region (e.g., us-east-1)
   - Choose "Serverless" option
4. Once created, go to database settings:
   - Find "Database ID" and "Region"
   - Generate an "Application Token"
   - Copy all three values

## Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 3: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file and fill in your credentials:
   ```env
   # Option A: direct Astra DB endpoint
   ASTRA_DB_API_ENDPOINT=https://your_db_endpoint
   ASTRA_DB_APPLICATION_TOKEN=your_token
   ASTRA_DB_KEYSPACE=default_keyspace

   # Option B: legacy ID/region form
   ASTRA_DB_ID=your_astra_db_id
   ASTRA_DB_REGION=your_region (e.g., us-east-1)
   ASTRA_DB_APPLICATION_TOKEN=your_token
   ASTRA_DB_KEYSPACE=default_keyspace
   
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-1.5-pro
   
   MISTRAL_API_KEY=your_mistral_api_key
   EMBEDDING_MODEL=mistral-embed
   ```

## Step 4: Run the API Server

From the `backend` directory:

```bash
# On Windows
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the batch file
run.bat
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Test the API

### Option 1: Using the Example Script

In another terminal, from the `backend` directory:

```bash
python example_usage.py
```

### Option 2: Using curl

```bash
# Check health
curl http://localhost:8000/health

# Upload text document
curl -X POST "http://localhost:8000/api/documents/upload-text" \
  -H "Content-Type: application/json" \
  -d "{
    \"filename\": \"test.txt\",
    \"content\": \"Your document content here\"
  }"

# Query the document (replace document_id)
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"Your question here\",
    \"top_k\": 3
  }"
```

### Option 3: Using Python Requests

```python
import requests

# Upload document
response = requests.post(
    "http://localhost:8000/api/documents/upload-text",
    json={
        "filename": "test.txt",
        "content": "Document content..."
    }
)
document_id = response.json()["document_id"]

# Query
response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "query": "Your question?",
        "document_id": document_id
    }
)
print(response.json()["answer"])
```

## Uploading Files

### PDF/TXT/MD Files

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@path/to/document.pdf"
```

Or using Python:

```python
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/documents/upload",
        files=files
    )
```

## Common Issues

### 1. "Module not found" errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### 2. Connection refused to Astra DB

- Verify your Astra DB credentials
- Check internet connection
- Ensure database is in "ACTIVE" state

### 3. Gemini API errors

- Verify API key is correct
- Check if you have Gemini API enabled
- Ensure you're not exceeding rate limits

### 4. No results from query

- Check if documents are uploaded
- Verify query is related to document content
- Try increasing `top_k` parameter

## Architecture

```
┌─────────────┐
│  Frontend   │
└──────┬──────┘
       │
┌──────▼──────────────────────────────┐
│         FastAPI Server              │
│  (app/main.py, app/routes/)         │
└──────┬──────────────────────────────┘
       │
       ├─────────────────────┬─────────────────────┐
       │                     │                     │
┌──────▼──────────┐  ┌──────▼──────┐   ┌─────────▼─────────┐
│ Document        │  │ Vector DB   │   │  Gemini LLM       │
│ Processor       │  │ (Astra DB)  │   │  Service          │
│ - Chunking      │  │ - Storage   │   │  - Answer Gen     │
│ - Embeddings    │  │ - Retrieval │   │  - Context Aware  │
└─────────────────┘  └─────────────┘   └───────────────────┘
```

## Next Steps

1. Upload your first document
2. Try different queries
3. Adjust chunking parameters if needed
4. Deploy to production (add authentication, use specific CORS origins)
5. Build a frontend application

## Support

For issues or questions:
1. Check the README.md for API documentation
2. Review the example_usage.py for usage patterns
3. Check logs from the server for detailed errors
