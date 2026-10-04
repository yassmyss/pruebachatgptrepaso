from typing import TypedDict

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.config import get_settings
from app.rag import build_retriever


class SupportState(TypedDict, total=False):
    question: str
    category: str
    documents: list[Document]
    answer: str


def classify(state: SupportState) -> SupportState:
    question = state["question"].lower()
    categories = {
        "network": ("dns", "internet", "wifi", "red", "ping", "conexión"),
        "containers": ("docker", "container", "contenedor", "wsl"),
        "database": ("postgres", "sql", "database", "base de datos"),
        "windows": ("windows", "servicio", "contraseña", "cuenta"),
        "storage": ("disco", "espacio", "storage"),
    }
    for category, keywords in categories.items():
        if any(keyword in question for keyword in keywords):
            return {"category": category}
    return {"category": "general"}


def retrieve(state: SupportState) -> SupportState:
    retriever = build_retriever()
    docs = retriever.invoke(state["question"])
    return {"documents": docs}


def answer(state: SupportState) -> SupportState:
    settings = get_settings()
    llm = ChatOpenAI(model=settings.openai_chat_model, temperature=0)
    context = "\n\n".join(
        f"[Fuente: {doc.metadata.get('source', 'desconocida')}]\n{doc.page_content}"
        for doc in state.get("documents", [])
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Eres un agente de soporte técnico N1/N2.
Responde únicamente con información respaldada por el contexto recuperado.
Si el contexto no es suficiente, indícalo y recomienda escalar la incidencia.
No inventes comandos, credenciales ni procedimientos.
Da pasos claros, seguros y verificables.""",
            ),
            (
                "human",
                "Categoría: {category}\nIncidencia: {question}\n\nContexto:\n{context}",
            ),
        ]
    )
    response = (prompt | llm).invoke(
        {
            "category": state.get("category", "general"),
            "question": state["question"],
            "context": context,
        }
    )
    return {"answer": response.content}


def create_graph():
    graph = StateGraph(SupportState)
    graph.add_node("classify", classify)
    graph.add_node("retrieve", retrieve)
    graph.add_node("answer", answer)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)
    return graph.compile()


support_graph = create_graph()
