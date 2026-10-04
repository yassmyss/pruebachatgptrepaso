from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings

KB_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"


def load_documents() -> list[Document]:
    documents: list[Document] = []
    for path in sorted(KB_DIR.glob("*.md")):
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": path.name},
            )
        )
    if not documents:
        raise RuntimeError("Knowledge base is empty.")
    return documents


def build_retriever():
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120)
    chunks = splitter.split_documents(load_documents())

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(\n            model=settings.openai_embedding_model,\n            api_key=settings.openai_api_key,\n        ),
        collection_name="support_knowledge",
    )
    return vector_store.as_retriever(search_kwargs={"k": settings.top_k})
