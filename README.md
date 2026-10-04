# SupportRAG Agent

> Agentic RAG assistant for IT support built with Python, LangChain, LangGraph, semantic search and a vector database.

SupportRAG Agent is a compact portfolio project that demonstrates how a support assistant can answer technical incidents using **retrieved evidence instead of relying only on an LLM's internal knowledge**.

The project is intentionally small: the goal is to make the architecture easy to understand, run and discuss in a technical interview.

## What it demonstrates

- Python backend development with **FastAPI**
- LLM integration
- **RAG (Retrieval-Augmented Generation)**
- embeddings and semantic search
- vector storage with **Chroma**
- document loading and retrieval with **LangChain**
- workflow orchestration with **LangGraph**
- grounded answers with source attribution
- Pydantic validation
- basic automated tests
- Docker packaging
- safe escalation when the knowledge base is insufficient

## Use case

A user reports an IT incident such as:

```text
Docker Desktop does not start after a Windows update and WSL shows an error.
```

Instead of asking the LLM to invent a generic solution, the application:

1. receives the incident through a REST API;
2. classifies the incident;
3. converts the query into an embedding;
4. performs semantic retrieval over the support knowledge base;
5. injects the relevant chunks into the LLM context;
6. generates a grounded troubleshooting response;
7. returns the answer together with the source documents.

If the retrieved information is insufficient, the prompt instructs the model to recommend escalation rather than fabricate a procedure.

## Architecture

```text
                 ┌──────────────┐
                 │    Client    │
                 └──────┬───────┘
                        │ POST /ask
                        ▼
                 ┌──────────────┐
                 │   FastAPI    │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │  LangGraph   │
                 │    State     │
                 └──────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      classify       retrieve       answer
                        │
                        ▼
                 ┌──────────────┐
                 │  LangChain   │
                 │  Retriever   │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │ Embeddings   │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │   Chroma     │
                 │ Vector Store │
                 └──────┬───────┘
                        ▼
                 Knowledge Base
```

## Why LangChain and LangGraph?

They solve different problems.

**LangChain** provides the RAG building blocks: documents, text splitting, embeddings, vector store integration and retrieval.

**LangGraph** controls the application workflow and state. The current MVP uses three explicit nodes:

```text
START -> classify -> retrieve -> answer -> END
```

This separation makes it straightforward to evolve the MVP into a more agentic system with conditional routing, tools, retries, confidence checks and human escalation.

## Project structure

```text
.
├── app/
│   ├── __init__.py
│   ├── config.py        # environment configuration
│   ├── graph.py         # LangGraph workflow
│   ├── main.py          # FastAPI endpoints
│   ├── rag.py           # ingestion, embeddings and retriever
│   └── schemas.py       # API models
├── knowledge_base/
│   ├── docker.md
│   ├── network.md
│   ├── postgresql.md
│   └── storage.md
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── Dockerfile
└── requirements.txt
```

## Quick start

### 1. Clone

```bash
git clone https://github.com/yassmyss/pruebachatgptrepaso.git
cd pruebachatgptrepaso
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env.example` to `.env` and add your API key.

```env
OPENAI_API_KEY=...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TOP_K=4
```

**Never commit the `.env` file or API keys.**

### 5. Run

```bash
uvicorn app.main:app --reload
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Example

Request:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Docker Desktop no arranca y WSL muestra un error. ¿Qué compruebo?\"}"
```

Response shape:

```json
{
  "category": "containers",
  "answer": "Pasos de diagnóstico basados en la documentación recuperada...",
  "sources": [
    {
      "source": "docker.md",
      "excerpt": "Docker Desktop / WSL..."
    }
  ]
}
```

## RAG flow

### Ingestion

Markdown documents are loaded from `knowledge_base/` and split into overlapping chunks.

### Embeddings

Each chunk is converted into a vector representation using an embedding model.

### Semantic retrieval

The user's incident is embedded and Chroma retrieves the closest chunks by semantic similarity.

This differs from keyword search: the query does not need to contain exactly the same words as the source document.

### Generation

Retrieved chunks are inserted into the prompt as context. The LLM is instructed to answer only from that evidence and to escalate when evidence is insufficient.

This is the **grounding** mechanism used to reduce hallucinations.

## API

### GET /health

Simple liveness endpoint.

### POST /ask

Input:

```json
{
  "question": "PostgreSQL refuses the application's connection. What should I check?"
}
```

Output:

- detected incident category;
- grounded answer;
- retrieved sources and excerpts.

## Testing

```bash
pytest
```

The initial test suite validates API health and request validation. A production evolution should add mocked LLM/retriever tests, retrieval evaluation and end-to-end tests.

## Docker

```bash
docker build -t support-rag-agent .
docker run --env-file .env -p 8000:8000 support-rag-agent
```

## Design decisions

### Why RAG instead of fine-tuning?

The problem is access to changing support documentation, not teaching the model a new language behaviour. RAG allows the knowledge base to be updated without retraining the model and makes source attribution possible.

### Why a vector database?

Traditional keyword matching can miss semantically equivalent questions. Embeddings represent meaning numerically and allow semantic similarity search.

### Why source attribution?

A support system should make its evidence inspectable. Returning sources helps a technician verify the proposed procedure.

### Why human escalation?

An enterprise support assistant should not pretend to know an answer when evidence is weak. Escalation is safer than hallucinating destructive commands or configuration changes.

## Current limitations

This is an MVP, not a production support platform.

- the knowledge base contains synthetic demonstration procedures;
- Chroma is created in memory when the retriever is built;
- there is no authentication or authorization;
- there is no ticketing-system integration;
- retrieval quality is not yet evaluated against a golden dataset;
- the graph currently has deterministic routing rather than autonomous tool selection.

These limitations are documented intentionally rather than hidden.

## Roadmap

- [ ] persistent Chroma or PostgreSQL + pgvector
- [ ] PDF/DOCX ingestion
- [ ] LangGraph conditional routing
- [ ] tool calling for safe diagnostic tools
- [ ] confidence/evidence evaluation node
- [ ] human-in-the-loop escalation
- [ ] ticket creation integration
- [ ] conversation memory
- [ ] retrieval evaluation / golden dataset
- [ ] observability and tracing
- [ ] AWS deployment (Bedrock/S3)
- [ ] CI pipeline with GitHub Actions

## Interview talking points

This project can be used to discuss:

- how embeddings enable semantic search;
- why chunk size and overlap affect retrieval;
- RAG vs fine-tuning;
- vector databases;
- hallucination reduction and grounding;
- LangChain vs LangGraph;
- stateful workflows and agents;
- API design with FastAPI;
- validation with Pydantic;
- testing and Docker;
- guardrails and human escalation;
- how the MVP could evolve for enterprise use.

## Security

The repository contains no credentials. Secrets are loaded through environment variables and `.env` is ignored by Git.

The sample knowledge base is synthetic and contains no real customer or company information.

## Author

Portfolio project focused on Python, Generative AI, RAG and agentic workflows.
