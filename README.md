# RAG Chatbot API

A Retrieval-Augmented Generation chatbot built with FastAPI, LangChain, and OpenAI. Supports dual retrieval strategies for A/B comparison: a standard chunking approach (v1) and a layout-aware hybrid retrieval approach (v2).

> **Automation:** Creating a Jira ticket automatically opens a PR implemented by
> Claude Code. See [`docs/jira-automation-setup.md`](docs/jira-automation-setup.md).

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   FastAPI    │────▶│  RAG Service  │────▶│   OpenAI     │
│   Routers   │     │  (LangChain)  │     │  gpt-4o-mini │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  FAISS   │ │   BM25   │ │ Ensemble │
        │(vectors) │ │(keywords)│ │ Retriever│
        └──────────┘ └──────────┘ └──────────┘
```

## Retrieval Strategies

| | Strategy v1 | Strategy v2 |
|---|---|---|
| **PDF Parsing** | LlamaIndex `SimpleDirectoryReader` | `pymupdf4llm` (layout-aware markdown) |
| **Chunking** | `SentenceSplitter` (1000 tokens, 200 overlap) | `MarkdownNodeParser` (heading boundaries) |
| **Retrieval** | FAISS similarity search | Hybrid: FAISS (0.6) + BM25 (0.4) via `EnsembleRetriever` |
| **Metadata** | Basic file info | Content type tagging (prose/code/table) |
| **FAISS Index** | `faiss_index_v1/` | `faiss_index_v2/` |

Pass `"strategy": "v1"` or `"strategy": "v2"` in request bodies to select.

## Project Structure

```
├── main.py                          # FastAPI app + lifespan startup
├── config.py                        # Settings (pydantic-settings, .env)
│
├── models/
│   ├── chat.py                      # ChatRequest, ChatResponse
│   └── document.py                  # IngestRequest, IngestResponse
│
├── routers/
│   ├── chat.py                      # POST /chat/message
│   └── documents.py                 # POST /documents/ingest
│
├── services/
│   ├── rag_service.py               # Retrieval + generation pipeline
│   ├── ingestion_service.py         # Dual-strategy document ingestion
│   ├── web_search.py                # OpenAI web search tool
│   ├── llm/                         # LLM providers (OpenAI)
│   ├── embeddings/                  # Embedding providers (OpenAI, Qwen)
│   └── vector_store/                # Vector store (FAISS + factory)
│
├── data/
│   ├── python/                      # Python documentation PDFs
│   └── kubernetes/                  # Kubernetes documentation PDFs
│
├── faiss_index_v1/                  # Persisted FAISS index (strategy v1)
├── faiss_index_v2/                  # Persisted FAISS index (strategy v2)
├── ingestion_cache/                 # LlamaIndex pipeline cache
│
└── next_steps/
    └── PLAN.md                      # Full roadmap and production plan
```

## Setup

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- OpenAI API key

### Install

```bash
git clone <repo-url>
cd ChatBot
poetry install
```

### Configure

Create a `.env` file:

```env
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
OPENAI_API_KEY=sk-your-key-here
```

### Run

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or via VS Code: use the included launch configuration (F5).

## API Endpoints

### Chat

```
POST /chat/message
```

```json
{
  "message": "What are Python decorators?",
  "strategy": "v1"
}
```

Response:

```json
{
  "reply": "Decorators are functions that wrap another function..."
}
```

The response includes a **Context Quality** self-assessment:
- **Summary** — what the retrieved context covers
- **Relevance** — High / Medium / Low with reasoning
- **What was missing** — if relevance is Medium or Low

### Document Ingestion

```
POST /documents/ingest
```

```json
{
  "directory": "data/python",
  "strategy": "v2"
}
```

Response:

```json
{
  "chunks_ingested": 142
}
```

### Interactive Docs

FastAPI auto-generates interactive API docs:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + uvicorn |
| LLM | OpenAI gpt-4o-mini (via LangChain) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | FAISS (faiss-cpu) |
| Keyword Search | BM25 (rank-bm25) |
| Hybrid Retrieval | LangChain EnsembleRetriever |
| PDF Parsing (v1) | LlamaIndex SimpleDirectoryReader + pypdf |
| PDF Parsing (v2) | pymupdf4llm (layout-aware markdown) |
| Chunking (v1) | LlamaIndex SentenceSplitter |
| Chunking (v2) | LlamaIndex MarkdownNodeParser |
| Web Search | OpenAI Responses API (web_search tool) |
| Config | pydantic-settings (.env) |

## Design Patterns

- **Factory + Singleton** — `@lru_cache` on `get_llm()`, `get_vector_store(strategy)`, `get_pipeline_v1/v2()` for efficient reuse
- **Strategy Pattern** — v1/v2 routing through request body, separate FAISS indexes, separate ingestion pipelines
- **Abstract Base Classes** — pluggable providers for LLM, embeddings, and vector store
- **Lifespan Startup** — all dependencies eagerly initialized at server start (no cold-start latency on first request)

## License

Private project.
