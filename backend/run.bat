@echo off
REM Start the RAG API server

echo Starting Knowledge Based RAG API...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
