# SupportRAG Agent

Sistema inteligente de soporte técnico basado en **RAG (Retrieval-Augmented Generation)** y orquestación mediante grafos. Recupera información relevante desde una base de conocimiento, genera respuestas fundamentadas en la documentación disponible y devuelve las fuentes utilizadas para facilitar su verificación.

Desarrollado en **Python** con **FastAPI, LangChain, LangGraph, embeddings, búsqueda semántica, Chroma y modelos de lenguaje (LLM)**.

## Objetivo

SupportRAG Agent plantea una arquitectura extensible para asistentes de soporte técnico N1/N2 capaces de:

- recibir incidencias mediante una API REST;
- clasificar la consulta;
- localizar procedimientos mediante búsqueda semántica;
- recuperar los fragmentos documentales más relevantes;
- generar respuestas contextualizadas mediante un LLM;
- identificar las fuentes utilizadas;
- limitar respuestas no respaldadas por la documentación;
- recomendar escalado cuando la información disponible no sea suficiente.

El modelo no actúa como única fuente de conocimiento: la respuesta se construye a partir de información recuperada de una base documental controlada.

## Arquitectura

```text
                         ┌──────────────────┐
                         │     Cliente      │
                         └────────┬─────────┘
                                  │ POST /ask
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │    LangGraph     │
                         │ Estado del flujo │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
               Clasificación  Recuperación  Generación
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    LangChain     │
                         │    Retriever     │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │    Embeddings    │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │      Chroma      │
                         │  Vector Store    │
                         └────────┬─────────┘
                                  ▼
                         Base de conocimiento
```

## Flujo de procesamiento

### 1. Recepción de la incidencia

FastAPI expone el endpoint `POST /ask`, que recibe una consulta técnica en lenguaje natural.

### 2. Clasificación

LangGraph inicia el flujo y asigna una categoría a la incidencia. El MVP contempla redes, contenedores, bases de datos, Windows, almacenamiento y categoría general.

### 3. Procesamiento documental

Los documentos Markdown de `knowledge_base/` se dividen mediante `RecursiveCharacterTextSplitter`.

Configuración actual:

- fragmentos de 700 caracteres;
- solapamiento de 120 caracteres.

El solapamiento ayuda a conservar contexto cuando una explicación queda dividida entre fragmentos.

### 4. Embeddings

Cada fragmento se transforma en una representación vectorial. Esto permite recuperar información por similitud semántica y no únicamente por coincidencia literal de palabras.

### 5. Base de datos vectorial

Los vectores se almacenan en **Chroma**. Ante una consulta, el sistema genera su embedding y recupera los fragmentos semánticamente más próximos.

El número de resultados puede configurarse mediante `TOP_K`.

### 6. Generación aumentada por recuperación

Los documentos recuperados se incorporan al contexto del LLM. El modelo recibe instrucciones para utilizar la evidencia disponible, no inventar procedimientos ni credenciales y recomendar escalado cuando el contexto sea insuficiente.

### 7. Respuesta y trazabilidad

La API devuelve:

- categoría detectada;
- respuesta generada;
- documentos utilizados;
- extractos de las fuentes recuperadas.

## LangChain

LangChain implementa los componentes principales del pipeline RAG:

- documentos;
- fragmentación de texto;
- embeddings;
- integración con Chroma;
- recuperación semántica;
- composición del prompt;
- integración con el LLM.

## LangGraph

LangGraph modela la ejecución como un grafo con estado.

```text
START
  │
  ▼
classify
  │
  ▼
retrieve
  │
  ▼
answer
  │
  ▼
 END
```

Esta separación permite evolucionar la arquitectura incorporando rutas condicionales, herramientas, reintentos, evaluación de evidencia y escalado sin concentrar toda la lógica en una única cadena.

## Estructura

```text
support-rag-agent/
├── app/
│   ├── __init__.py
│   ├── config.py        # Configuración
│   ├── graph.py         # Flujo LangGraph
│   ├── main.py          # API FastAPI
│   ├── rag.py           # Ingesta, embeddings y recuperación
│   └── schemas.py       # Modelos Pydantic
├── knowledge_base/
│   ├── docker.md
│   ├── network.md
│   ├── postgresql.md
│   └── storage.md
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── Dockerfile
├── README.md
└── requirements.txt
```

## Tecnologías

| Tecnología | Función |
|---|---|
| Python | Lenguaje principal |
| FastAPI | API REST |
| Pydantic | Validación y modelos de datos |
| LangChain | Pipeline RAG |
| LangGraph | Orquestación y estado |
| OpenAI | LLM y embeddings |
| Chroma | Base de datos vectorial |
| pytest | Pruebas automatizadas |
| Docker | Contenerización |

## Instalación

### Requisitos

- Python 3.11 o superior
- pip
- clave de API del proveedor LLM
- Docker opcional

### Clonar

```bash
git clone https://github.com/yassmyss/support-rag-agent.git
cd support-rag-agent
```

### Entorno virtual

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

### Dependencias

```bash
pip install -r requirements.txt
```

### Variables de entorno

Crear `.env` a partir de `.env.example`:

```env
OPENAI_API_KEY=tu_clave
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TOP_K=4
```

Las credenciales nunca deben almacenarse en el repositorio.

## Ejecución

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Documentación OpenAPI:

```text
http://127.0.0.1:8000/docs
```

## API

### Estado

```http
GET /health
```

```json
{
  "status": "ok"
}
```

### Consulta

```http
POST /ask
Content-Type: application/json
```

Entrada:

```json
{
  "question": "Docker Desktop no arranca y WSL muestra un error. ¿Qué debería comprobar?"
}
```

Salida:

```json
{
  "category": "containers",
  "answer": "Respuesta generada a partir de la documentación recuperada.",
  "sources": [
    {
      "source": "docker.md",
      "excerpt": "Fragmento documental utilizado como contexto..."
    }
  ]
}
```

## Ejemplo con cURL

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Docker Desktop no arranca y WSL muestra un error. ¿Qué compruebo?\"}"
```

## Funcionamiento del RAG

```text
Consulta
   │
   ▼
Embedding
   │
   ▼
Búsqueda semántica
   │
   ▼
Fragmentos relevantes
   │
   ▼
Contexto + consulta
   │
   ▼
LLM
   │
   ▼
Respuesta fundamentada
```

Una llamada directa a un LLM depende principalmente del conocimiento contenido en el modelo. El enfoque RAG incorpora conocimiento externo y actualizable antes de generar la respuesta.

### ¿Por qué RAG y no fine-tuning?

El objetivo es consultar documentación técnica que puede cambiar.

RAG permite:

- actualizar el conocimiento modificando los documentos;
- mantener la información separada del modelo;
- recuperar evidencia concreta;
- proporcionar trazabilidad mediante fuentes;
- reducir respuestas no fundamentadas.

El fine-tuning resulta más adecuado para modificar comportamientos o patrones especializados del modelo que para mantener una base documental dinámica.

## Búsqueda semántica

Los embeddings permiten aproximar textos por significado.

Por ejemplo:

```text
"no puedo abrir Docker después de actualizar Windows"
```

puede recuperar documentación relativa a:

```text
"Docker Desktop no inicia / problemas con WSL"
```

aunque las expresiones no coincidan literalmente.

## Base de conocimiento

El MVP incluye documentación sintética sobre:

- Docker Desktop y WSL;
- conectividad y DNS;
- PostgreSQL;
- almacenamiento y espacio en disco.

No contiene datos de clientes, organizaciones ni sistemas reales.

La arquitectura puede ampliarse para ingerir PDF, DOCX, HTML, bases de datos, APIs o repositorios documentales.

## Seguridad

Medidas incorporadas:

- credenciales mediante variables de entorno;
- `.env` excluido del control de versiones;
- ausencia de credenciales en la base documental;
- instrucciones para evitar procedimientos no documentados;
- prohibición de mostrar credenciales;
- escalado cuando la evidencia resulte insuficiente;
- documentación de demostración sintética.

En producción deberían incorporarse autenticación, autorización, auditoría, control de acceso documental, protección frente a prompt injection y políticas específicas para información sensible.

## Pruebas

```bash
pytest
```

La versión actual comprueba:

- disponibilidad del endpoint de salud;
- validación de solicitudes incorrectas.

La evolución del proyecto contempla pruebas unitarias del grafo, mocks del LLM, evaluación del retriever y pruebas end-to-end.

## Docker

Construcción:

```bash
docker build -t support-rag-agent .
```

Ejecución:

```bash
docker run --env-file .env -p 8000:8000 support-rag-agent
```

## Limitaciones actuales

El proyecto se encuentra en fase MVP:

- base documental de demostración sintética;
- almacén vectorial generado durante la ejecución;
- sin autenticación;
- sin integración con plataforma de tickets;
- sin memoria conversacional;
- sin dataset específico de evaluación RAG;
- clasificación inicial basada en reglas;
- sin ejecución de herramientas externas.

Estas limitaciones delimitan el alcance actual y sirven como base para las siguientes iteraciones.

## Evolución prevista

- persistencia del índice vectorial;
- PostgreSQL + pgvector;
- ingesta de PDF, DOCX y otras fuentes;
- rutas condicionales en LangGraph;
- evaluación automática de relevancia;
- reescritura de consultas cuando la recuperación sea insuficiente;
- herramientas de diagnóstico controladas;
- escalado human-in-the-loop;
- integración con sistemas de tickets;
- memoria conversacional;
- dataset de evaluación RAG;
- observabilidad y trazabilidad;
- autenticación y autorización;
- despliegue cloud;
- AWS S3 y Amazon Bedrock;
- CI/CD.

## Principios de diseño

### Respuestas fundamentadas

La generación debe priorizar la evidencia recuperada frente a información no verificable del modelo.

### Trazabilidad

Las fuentes utilizadas forman parte de la respuesta.

### Separación de responsabilidades

API, recuperación documental y orquestación se mantienen desacopladas.

### Extensibilidad

La arquitectura basada en grafos permite añadir etapas y decisiones sin rediseñar el sistema completo.

### Seguridad

Ante falta de evidencia, el sistema debe reconocer la limitación y escalar en lugar de generar instrucciones potencialmente incorrectas.

## Estado del proyecto

**Versión:** 0.1.0  
**Estado:** MVP funcional · evolución activa  
**Ámbito:** IA generativa · RAG · agentes · automatización de soporte técnico
