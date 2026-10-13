# Memo API

A FastAPI service that stores personal memos and answers natural-language questions about them
using RAG with a local LLM (Ollama). Includes JWT authentication with per-user memo isolation.

Ask a question in natural language and the app answers from your memos
(UI is in Korean: "오늘 회의 몇시야?" = "What time is today's meeting?" → "The meeting is at 3 PM").

![App screenshot](docs/app.png)

![API docs](docs/swagger.png)

## Features

- JWT authentication with registration and login
- Memo CRUD with per-user access control (other users' memos return 403)
- Natural-language Q&A over your memos using RAG with a local LLM
- 9 automated tests with pytest covering auth, permissions, and memo creation

## Tech Stack

- Backend: Python, FastAPI, Uvicorn
- Database: SQLite, SQLAlchemy
- Auth: JWT (python-jose), bcrypt (passlib)
- AI/RAG: Ollama (llama3.1:8b, kure-v1 embeddings), LangChain, Chroma
- Testing: pytest, httpx
- Frontend: React (CDN), JavaScript

## Getting Started

1. Install [Ollama](https://ollama.com) and pull the models
```bash
   ollama pull llama3.1:8b
   ollama pull daynice/kure-v1
```
2. Create a virtual environment and install dependencies
```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```
3. Start the server
```bash
   uvicorn main:app --reload
```
4. Open the API docs at http://127.0.0.1:8000/docs
5. Open `frontend/app.html` in a browser for the React UI

## Running Tests

```bash
pytest
```