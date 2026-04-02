# 📄 PDF Q&A Engine - RAG Pipeline

A production-style backend that lets users **upload any PDF and ask natural-language questions** about it. Built on a Retrieval-Augmented Generation (RAG) architecture using **FastAPI**, **Qdrant**, **Google Gemini embeddings**, and **LangChain** - designed for accuracy, speed, and clean API design.

> Answers are always grounded in the document. If the information isn't there, the system says so - no hallucinations.

---

## 🏗️ Architecture

```
User uploads PDF
      │
      ▼
 FastAPI /upload endpoint
      │
      ▼
 PyPDFLoader  ──▶  RecursiveCharacterTextSplitter (1000 tokens, 400 overlap)
      │
      ▼
 Gemini Embedding Model (gemini-embedding-001)
      │
      ▼
 Qdrant Vector DB  (Docker)
      │
User asks question ──▶  FastAPI /ask endpoint
                              │
                        Similarity Search (Qdrant)
                              │
                        Top-k Chunks + Page Numbers
                              │
                        Gemini 2.5 Flash (LLM)
                              │
                     Grounded Answer + Page Reference
```

---

## ✨ Features

- 📤 **PDF ingestion** via REST API - upload any PDF and it's chunked and indexed instantly
- 🔍 **Semantic search** using Google Gemini embeddings stored in Qdrant vector DB
- 🤖 **Grounded Q&A** - answers reference exact page numbers from your document
- 🚫 **Hallucination-resistant** - responds with "Not found in document" when the answer isn't in context
- 🐳 **Dockerized vector DB** - Qdrant runs as a container, zero local setup required
- ⚡ **FastAPI backend** - async-ready, auto-documented at `/docs`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Vector Database | Qdrant (Docker) |
| Embeddings | Google Gemini (`gemini-embedding-001`) |
| LLM | Google Gemini 2.5 Flash |
| RAG Orchestration | LangChain |
| PDF Parsing | PyPDFLoader |
| Containerization | Docker Compose |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Google API Key ([get one here](https://aistudio.google.com/app/apikey))

### 1. Clone the repository

```bash
git clone https://github.com/your-username/RAG-pipeline.git
cd RAG-pipeline
```

### 2. Set up environment variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Start the Qdrant vector database

```bash
docker-compose -f app/docker-compose.yml up -d
```

This starts Qdrant on `http://localhost:6333`.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the API server

```bash
uvicorn app.main:app --reload
```

The API will be live at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## 📡 API Reference

### `POST /upload`
Upload and index a PDF file.

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your_document.pdf"
```

**Response:**
```json
{
  "message": "PDF indexed successfully"
}
```

---

### `GET /ask`
Ask a natural-language question about the uploaded document.

```bash
curl "http://localhost:8000/ask?question=What%20is%20the%20main%20topic%20of%20chapter%203"
```

**Response:**
```json
{
  "question": "What is the main topic of chapter 3?",
  "answer": "Chapter 3 covers retrieval mechanisms in transformer architectures. For more details, see page 42."
}
```

---

## 📁 Project Structure

```
RAG-pipeline/
├── app/
│   ├── main.py              # FastAPI routes (/upload, /ask)
│   ├── rag.py               # Core RAG logic: indexing + querying
│   └── docker-compose.yml   # Qdrant vector DB service
├── uploads/                 # Uploaded PDFs stored here
├── requirements.txt
├── .env                     # API keys (never commit this)
├── .gitignore
└── README.md
```

---

## ⚙️ How It Works

### Indexing (on PDF upload)
1. **Load** - PyPDFLoader reads the PDF page by page
2. **Chunk** - RecursiveCharacterTextSplitter splits text into 1000-token chunks with 400-token overlap to preserve context across boundaries
3. **Embed** - Each chunk is converted to a dense vector using Gemini's embedding model
4. **Store** - Vectors + metadata (page numbers) are stored in Qdrant

### Querying (on question)
1. **Embed query** - The user's question is converted to a vector using the same embedding model
2. **Retrieve** - Qdrant performs cosine similarity search and returns the top-k most relevant chunks
3. **Generate** - Chunks + page references are passed to Gemini 2.5 Flash as context
4. **Respond** - The LLM answers strictly from context, citing page numbers

