# 🧠 AI Knowledge Assistant

A personal AI-powered knowledge assistant that lets you upload your documents and chat with them using Retrieval-Augmented Generation (RAG). Every answer includes exact citations with page and section references.

---

## 🚀 Quick Start (Easiest Way)

You can run the entire app locally in two easy steps:

### 1. Start the Backend
Open a PowerShell terminal and run:
```powershell
.\start-backend.ps1
```
> The API will be available at **http://127.0.0.1:8000** (interactive docs at `http://127.0.0.1:8000/docs`).  
> *Note: It uses built-in SQLite automatically, so no database installation is required.*

### 2. Start the Frontend
Open a second PowerShell terminal and run:
```powershell
.\start-frontend.ps1
```
> The web application will open at **http://localhost:5173**.

Visit **[http://localhost:5173](http://localhost:5173)** in your browser to create an account and start uploading documents!

---

## ✨ Features

- 📄 **Multi-Format Uploads**: Supports PDF, Word (`.docx`), PowerPoint (`.pptx`), Markdown (`.md`), and plain text (`.txt`).
- 💬 **Grounded AI Chat**: Ask questions across your documents. The AI answers only from your uploaded materials.
- 🔍 **Clickable Citations**: Every answer provides citations linking back to the exact document and page/slide.
- 📊 **Study & Knowledge Tools**:
  - **Summary**: Generate executive summaries of documents.
  - **Comparison**: Compare concepts between different uploaded files.
  - **Quiz Generator**: Test your understanding with auto-generated practice quizzes.
- 🔐 **Privacy & Security**: Secure user registration, password hashing (Argon2), JWT authentication, and isolated data per user.

---

## 🛠️ Tech Stack

```
                          ┌──────────────────────────────────────────────┐
                          │         React 18 + TypeScript + Vite         │
                          │   (Tailwind CSS, TanStack Query, shadcn/ui)  │
                          └──────────────────────┬───────────────────────┘
                                                 │
                                                 │ HTTPS / JSON REST API
                                                 ▼
                          ┌──────────────────────────────────────────────┐
                          │           FastAPI Backend Server             │
                          │   (Auth, Document Pipeline, RAG Engine)      │
                          └──────────┬──────────────┬─────────────┬──────┘
                                     │              │             │
                    File Uploads     │  Vectors &   │             │ Async Tasks
                                     ▼  Full-Text   ▼             ▼
                              ┌────────────┐ ┌─────────────┐ ┌─────────────┐
                              │ S3 / MinIO │ │ PostgreSQL  │ │    Redis    │
                              │  Storage   │ │ + pgvector  │ │Task Queue   │
                              └────────────┘ └─────────────┘ └──────┬──────┘
                                                                    │
                                                                    ▼
                                                             ┌─────────────┐
                                                             │Celery Worker│
                                                             │(OCR/Parsers)│
                                                             └─────────────┘
```

---

## 📂 Project Structure

```text
ai-knowledge-assistant/
├── backend/            # FastAPI Python backend
│   ├── app/            # API routes, RAG engine, database models & parsers
│   └── tests/          # Automated backend test suite
├── frontend/           # React + TypeScript frontend
│   └── src/            # Pages, UI components, API services
├── start-backend.ps1   # Helper script to launch backend
├── start-frontend.ps1  # Helper script to launch frontend
└── test-all.ps1        # Runs all test suites
```

---

## 💻 Manual Setup (Alternative)

If you prefer running commands manually without the helper scripts:

### Backend
```bash
cd backend
python -m venv venv

# Activate venv:
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Running Tests

To verify that everything is working properly:

```bash
# Run all automated tests:
.\test-all.ps1

# Or test backend individually (22 tests):
cd backend
pytest -v

# Or test frontend individually:
cd frontend
npm test
```
