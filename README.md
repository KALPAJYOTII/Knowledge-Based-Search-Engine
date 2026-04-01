# Knowledge Based Search Engine

## Overview
### Techstack used

#### Frontend
- React
#### Backend
- FastAPI
#### LLM
- Gemini 2.5 Flash
#### Vector Database
- AstraDB


## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation

#### Clone the Repo
```bash
git clone https://github.com/KALPAJYOTII/Knowledge-Based-Search-Engine.git
```

#### Backend (FastAPI)
1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Make in .env file and set Environment variables according to the .env.example

4. Run the server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`

#### Frontend (React)
1. Navigate to the frontend directory:
```bash
cd frontend\Knowledge Based Answering RAG
```

2. Install dependencies:
```bash
npm install
```
3. Make in .env file and set Environment variables according to the .env.example

4. Start the development server:
```bash
npm run dev
```
The app will open at `http://localhost:5173`

