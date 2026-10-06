# Specification — Design

**Derived from:** `CONSTITUTION.C.md` (§11–§17, §19)
**Stack:** Python · OpenAI (chat + embeddings) · Chroma (local, persistent) · CLI

---

## 1. Architecture Overview

```text
CLI (main.py)
   │  user text
   ▼
Agent (agent/agent.py)  ← system instructions (prompts.py), state (state.py)
   │
   ├──► LLM Client (llm/client.py) ──── messages + tool schemas ───► OpenAI
   │         ▲                                      │
   │         │         tool calls / final text     │
   │         └──────────────────────────────────────┘
   │
   ├──► Retriever (rag/retriever.py) ── only when LLM calls search_knowledge
   │         └── embeddings.py (chromadb ONNX all-MiniLM-L6-v2)
   │              └── vector_store.py (Chroma, cosine)
   │
   └──► Calculator (tools/calculator.py) ── only when tool needed
              └── validate → execute → result
```

Dependency direction: `main → agent → {llm, rag, tools}` · `config` and `utils`
are leaf modules imported by everyone. Nothing imports `main`.

---

## 2. Module Contracts

### `config/settings.py`
```python
@dataclass(frozen=True)
class Settings:
    llm_model: str            # e.g. "gpt-4o-mini"
    embedding_model: str      # "text-embedding-3-small"
    llm_api_key: str          # from env, never logged
    chroma_path: Path         # default "./.chroma"
    knowledge_dir: Path       # default "./knowledge"
    retrieval_top_k: int      # default 4
    log_level: str            # default "INFO"
    max_tool_iterations: int  # default 5

def load_settings() -> Settings   # reads env once; raises ConfigError on missing key
```
No business logic (§17). Never prints or logs `llm_api_key` (§10).

### `llm/client.py`
```python
@dataclass
class LLMResponse:
    text: str | None
    tool_calls: list[ToolCall]   # name + raw arguments dict

class LLMClient:
    def chat(self, messages: list[Message], tools: list[dict] | None = None) -> LLMResponse
```
Wraps OpenAI errors into `LLMError` subclasses: `AuthError`, `TimeoutError`,
`RateLimitError`, `MalformedResponseError` (§12). Contains no policies (§17).

### `agent/state.py`
```python
@dataclass
class ConversationState:
    messages: list[Message]        # role, content, tool_calls, tool_call_id
    retrieved_context: str         # per-turn; cleared each turn
    turn_count: int
    metadata: dict                 # tools_used, retrieval_performed
```
Data only — no behavior, no I/O (§17).

### `agent/prompts.py`
```python
SYSTEM_INSTRUCTIONS: str                     # template, no business facts (§5)
def build_messages(system: str, history: list[dict]) -> list[dict]
```

### `agent/agent.py`
```python
class SupportAgent:
    def __init__(self, llm, settings, tools: dict[str, Tool], system=SYSTEM_INSTRUCTIONS)
    def run(self, user_text: str) -> str     # full orchestration loop (§4, §9)

def build_tools(retriever: Retriever | None) -> dict[str, ToolFunc]
def create_agent(settings) -> SupportAgent   # wires llm + retriever + tools
```
Loop: append user msg → LLM → (tool call? validate+execute → LLM) →
final text. Bounded by `max_tool_iterations` (§4). The `search_knowledge`
tool is registered only when the vector store opens successfully.
Logs each step (§13).

### `rag/`
```python
# ingestion.py
def load_documents(dir: Path) -> list[Document]
def clean(text: str) -> str
def chunk(text: str, size: int = 800, overlap: int = 150) -> list[Chunk]

# embeddings.py
class Embedder:
    def embed_texts(texts: list[str]) -> list[list[float]]
    def embed_query(text: str) -> list[float]
    # backend: chromadb ONNX (all-MiniLM-L6-v2, local, free)

# vector_store.py
class VectorStore:            # Chroma wrapper, persistent at settings.chroma_path
    def add(self, chunks: list[Chunk], embeddings) -> None
    def query(self, embedding, k: int) -> list[ScoredChunk]
    def reset(self) -> None   # for repeatable ingestion (§6.1)

# retriever.py
class Retriever:
    def search(self, query: str) -> list[ScoredChunk]   # score >= min_score only
    def format_context(self, chunks: list[ScoredChunk]) -> str  # sources included
```
Ingestion is offline and repeatable via `scripts/ingest.py` (§6.1).
Retrieval returns `None` on weak scores → agent uses honest-limitation path (§7).

### `tools/calculator.py`
```python
class CalculatorError(Exception): ...

def validate(expression: str) -> str   # whitelist: numbers, + - * / % ( ) . **
def evaluate(expression: str) -> str   # validate → ast-safe eval → formatted result
```
Pure function, no I/O, deterministic, independently testable (§8).
Tool schema exposed to the LLM:
```json
{"name": "calculator", "parameters": {"expression": {"type": "string"}}}
```
Whitelist of callable tools lives in the agent: `{"calculator": evaluate}` —
the LLM cannot invoke anything else (§8, §9).

### `utils/logging.py`
```python
def setup_logging(level: str) -> None      # console format, no secrets (§10)
def log_event(name: str, **fields) -> None # request_received, llm_completed, ...
```

---

## 3. Data Structures

```text
Message      = {role: "system"|"user"|"assistant"|"tool", content, tool_calls?, tool_call_id?}
ToolCall     = {id, name, arguments: dict}
Chunk        = {id, text, source_file, index}
ScoredChunk  = {chunk, score}
Document     = {source_file, text}
```

Vector: `text-embedding-3-small` → 1536 floats, stored in Chroma with
`chunk.id` as key and `source_file` as metadata.

---

## 4. Runtime Sequence

```text
User "What is 49 × 3?"
 → agent appends user message
 → LLM returns tool_call: calculator("49 * 3")
 → agent validates arguments          (fail → error text back to LLM)
 → agent executes evaluate(...)       → "147"
 → agent appends tool message
 → LLM returns: "The total is 147."
 → agent clears retrieved_context, updates state, returns text

User "What's your refund window?"
 → LLM returns tool_call: search_knowledge("refund window")
 → agent embeds query → Chroma top-k → chunks with score >= 0.3
 → agent returns formatted chunks as tool message
 → LLM returns grounded answer, or the refusal sentence when the tool
   reported no relevant information (§7)
```

---

## 5. Configuration Keys (§11)

| Env var | Purpose | Default |
|---|---|---|
| `LLM_API_KEY` | OpenAI key (secret) | — required |
| `LLM_MODEL` | chat model | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | embedding model | `text-embedding-3-small` |
| `CHROMA_PATH` | vector store dir | `./.chroma` |
| `KNOWLEDGE_DIR` | documents dir | `./knowledge` |
| `RETRIEVAL_TOP_K` | chunks per query | `4` |
| `RETRIEVAL_MIN_SCORE` | cosine score cutoff | `0.3` |
| `EMBEDDING_PROVIDER` | embeddings backend | `chromadb` |
| `EMBEDDING_MODEL` | embedding model | `all-MiniLM-L6-v2` |
| `MAX_TOOL_ITERATIONS` | loop bound | `5` |
| `LOG_LEVEL` | logging level | `INFO` |

`.env.example` lists all of these with placeholder values (§10).

---

## 6. Error Model (§12)

| Failure | Handling |
|---|---|
| Missing/invalid API key | Friendly config message at startup; no crash loop |
| LLM timeout / rate limit | Retry once with backoff → user-facing apology |
| Malformed LLM response | Log raw safely → ask user to rephrase |
| Chroma failure | Log → knowledge path unavailable message, chat still works |
| Invalid tool arguments | Tool error string returned to LLM for recovery |
| No relevant knowledge | Honest-limitation sentence (§7) |
| Empty user input | Prompt to rephrase (§12) |

Users see understandable messages; stack traces and secrets stay in logs.

---

## 7. Dependency Set (§16)

| Package | Justification |
|---|---|
| `openai` | official SDK; works with OpenAI, Groq, Ollama (compatible endpoints) |
| `chromadb` | local persistent vector store + ONNX embedding backend, no server |
| `pytest` | tests (dev) |

Stdlib covers: `ast` (safe calculator eval), `logging`, `dataclasses`,
`pathlib`, `re`, `http.server` (localhost UI). No framework in V1 (§2.2).
Note: `sentence-transformers` is not usable on this machine — an Application
Control policy blocks a scikit-learn DLL it requires; the chromadb ONNX
backend embeds the same model (`all-MiniLM-L6-v2`) without it.

---

## 8. Directory Layout (§18)

```text
customer-support-agent/
├── CONSTITUTION.C.md
├── README.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── skills.md · agents.md · spec/{requirements,design,milestones}.md
├── src/customer_support_agent/
│   ├── __init__.py · main.py
│   ├── agent/{__init__,agent,prompts,state}.py
│   ├── llm/{__init__,client}.py
│   ├── rag/{__init__,ingestion,embeddings,retriever,vector_store}.py
│   ├── tools/{__init__,calculator}.py
│   ├── config/{__init__,settings}.py
│   └── utils/{__init__,logging}.py
├── knowledge/{company,products,refund-policy}.md
├── tests/{test_agent,test_rag,test_tools}.py
└── scripts/ingest.py
```

No empty modules created just to match the diagram (§18).

---

## 9. Priority Order (§19)

```text
Correct agent behavior > Clean architecture > Tests > API > UI
```

V1 stops at Tests. FastAPI is a future layer only (§27, V5).
