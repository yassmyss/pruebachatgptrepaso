from fastapi import FastAPI

from app.graph import support_graph
from app.schemas import AskRequest, AskResponse, Source

app = FastAPI(
    title="SupportRAG Agent",
    version="0.1.0",
    description="Agentic RAG API for grounded IT support.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    result = support_graph.invoke({"question": payload.question})
    sources = [
        Source(
            source=doc.metadata.get("source", "unknown"),
            excerpt=doc.page_content[:280].replace("\n", " "),
        )
        for doc in result.get("documents", [])
    ]
    return AskResponse(
        category=result.get("category", "general"),
        answer=result["answer"],
        sources=sources,
    )
