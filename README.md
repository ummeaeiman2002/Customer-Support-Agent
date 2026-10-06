# AI Customer Support & Knowledge Agent

A reusable, portfolio-quality AI agent that answers customer questions using
an LLM, a local RAG knowledge base, and tools — while refusing to invent
company information it cannot verify.

Built as a learning project and a foundation for future AI automation work.

---

## The Problem

Customer support answers must be **accurate and grounded**. Raw LLM chatbots
fail in two ways:

1. They hallucinate company facts (prices, policies, refund rules) with
   confident wording.
2. They have no mechanism to look up authoritative information.

This agent solves both: it retrieves answers from a company knowledge base
before responding, and it explicitly says when the information isn't there.

## Features

- **Grounded answers** — company facts come only from retrieved documents
- **Honest limitation** — clear refusal when the knowledge base has no answer
  instead of a fabricated one
- **Tool calling** — calculator for arithmetic; retrieval itself is a tool
  the LLM decides when to use (no blind retrieval)
- **Local, free RAG** — Chroma vector store + ONNX embeddings
  (`all-MiniLM-L6-v2`) running on your machine, no embedding API costs
- **Provider-agnostic LLM** — Groq (free), OpenAI, or Ollama via one env var
- **Web UI + CLI** — three-column support dashboard (chat, knowledge browser,
  quick actions) and a terminal chat
- **Knowledge Base page** — browse company documents and run the same vector
  search the agent uses
- **API docs** — auto-generated Swagger UI at `/docs`
- **Safe tool execution** — AST-based calculator, argument validation,
  whitelisted tools only, bounded tool loops

## Architecture

```text
User (CLI or browser)
   ↓
Agent (orchestration loop)
   ├──► LLM Client ──────────► Groq / OpenAI / Ollama
   │      ▲                         │
   │      └──── tool calls ─────────┘
   │              │
   │   ┌──────────┴───────────┐
   │   ▼                      ▼
   │ calculator          search_knowledge
   │ (AST-safe eval)          │
   │                          ▼
   │                 Retriever → Embedder (ONNX) → Chroma
   │                          ▲
   └──────────────────────────┘   knowledge/*.md → ingestion → vectors
```

```text
backend/customer_support_agent/
├── agent/     agent.py (loop), prompts.py (instructions), state.py
├── llm/       client.py (OpenAI-compatible API wrapper)
├── rag/       ingestion.py, embeddings.py, vector_store.py, retriever.py
├── tools/     calculator.py
├── config/    settings.py (env-driven configuration)
├── utils/     logging.py
└── server.py  FastAPI app (chat API, knowledge API, static UI, Swagger)

frontend/
├── index.html   three-column layout
├── styles.css   navy/blue design system
└── app.js       chat state, knowledge base, API layer

knowledge/       company documents (RAG source)
```

## Workflow

```text
User question
   ↓
LLM with system instructions + conversation state
   ↓
┌──────────────────────────────────────┐
│ needs arithmetic?   → calculator     │
│ needs company fact? → search_knowledge│
│ otherwise           → answer directly│
└──────────────────────────────────────┘
   ↓
tool results back to the LLM (bounded loop)
   ↓
Grounded final response — or the honest "I couldn't find that information"
```

## RAG Pipeline

**Ingestion** (repeatable, offline):

```text
knowledge/*.md → load → clean → chunk → embed → Chroma (cosine)
```

**Runtime** (only when the LLM asks):

```text
query → embed → top-k vector search → score ≥ threshold
     → chunks with source refs as tool result → LLM → grounded answer
```

The full knowledge base is never sent to the LLM — only relevant chunks.

## Tool Calling

```text
User: What is 49 × 3?
Agent → validate args → calculator("49 * 3") → "147"
Agent → "The total is 147."

User: What is your refund window?
Agent → search_knowledge("refund window") → [refund-policy.md] ...
Agent → "You can request a refund within 30 days of delivery."
```

Tools are whitelisted; the LLM cannot invent callable functions. Arguments
are validated before execution, and the tool loop is bounded by
`MAX_TOOL_ITERATIONS`.

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.10+ | clarity and ecosystem |
| LLM | Groq `openai/gpt-oss-120b` (free tier) | free, fast, tool calling |
| Vector store | Chroma (local, persistent) | no server, simple |
| Embeddings | `all-MiniLM-L6-v2` via ONNX | local, free, no API |
| Backend | FastAPI + uvicorn | typed API, free Swagger docs |
| Frontend | vanilla HTML/CSS/JS | zero frameworks, no build step |
| Tests | pytest | simple, mocks for all live calls |

Any OpenAI-compatible endpoint works by changing `.env`
(`LLM_PROVIDER`: `groq` | `openai` | `ollama`).

## Example Conversations

```text
You: What is your refund window?
Agent: You can request a refund within 30 days of delivery.

You: What is 49 * 3?
Agent: The result is 147.

You: What is your CEO's favorite color?
Agent: I couldn't find that information in the available company knowledge base.

You: How much does the AuroraBuds Pro cost?
Agent: The AuroraBuds Pro costs $129.00.
```

## Installation

```bash
git clone https://github.com/ummeaeiman2002/Customer-Support-Agent.git
cd Customer-Support-Agent

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -e ".[dev]"

copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
```

Edit `.env` and set your free Groq key:

```text
LLM_API_KEY=gsk_your_free_key        # console.groq.com -> API Keys
```

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `LLM_PROVIDER` | `groq` | `groq`, `openai`, or `ollama` |
| `LLM_MODEL` | `openai/gpt-oss-120b` | chat model name |
| `LLM_API_KEY` | — | key for groq/openai (never commit `.env`) |
| `GROQ_BASE_URL` | Groq endpoint | OpenAI-compatible base URL |
| `EMBEDDING_PROVIDER` | `chromadb` | embeddings backend |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | embedding model |
| `KNOWLEDGE_DIR` | `./knowledge` | company documents |
| `CHROMA_PATH` | `./.chroma` | vector store location |
| `RETRIEVAL_TOP_K` | `4` | chunks per search |
| `RETRIEVAL_MIN_SCORE` | `0.3` | similarity cutoff |
| `MAX_TOOL_ITERATIONS` | `5` | tool loop bound |
| `HOST` / `PORT` | `127.0.0.1` / `8000` | web UI bind |
| `LOG_LEVEL` | `INFO` | logging verbosity |

## Usage

```bash
# 1. Ingest the knowledge base (repeatable)
python scripts/ingest.py

# 2a. Web UI
python -m customer_support_agent.server
#    → chat:    http://127.0.0.1:8000
#    → API docs: http://127.0.0.1:8000/docs

# 2b. CLI
python -m customer_support_agent.main
```

**Web UI** — three-column support dashboard: sidebar navigation, chat with
the live agent, knowledge-base browser, quick actions.

**HTTP API:**

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/chat` | POST | `{"message": "..."}` → `{"reply": "..."}` |
| `/api/reset` | POST | reset conversation state |
| `/api/knowledge` | GET | list knowledge documents |
| `/api/knowledge/{name}` | GET | read one document |
| `/api/knowledge/search?q=` | GET | vector search over the knowledge base |

Changing businesses = edit `knowledge/*.md` + re-run ingestion. The agent
core is untouched.

## Testing

```bash
pytest
```

42 tests, all offline (live APIs mocked): calculator (valid/invalid/edge),
settings and secret handling, agent loops (normal/tool/knowledge/unknown/
bounded), ingestion, vector store, retrieval thresholds (§14).

## Security

- Secrets live only in `.env` (git-ignored); `.env.example` documents them
- API keys never appear in logs or `repr()` output
- Calculator uses AST whitelisting — no arbitrary code execution
- User-facing errors never expose stack traces or internals

## Limitations

- Single-turn knowledge per question; no long-term memory (V1 scope)
- Local demo only — not deployed, not production-hardened
- No authentication, rate limiting, or multi-user support
- Embeddings are fixed to `all-MiniLM-L6-v2` (chromadb ONNX backend)
- `sentence-transformers` unusable on this machine (Application Control
  policy blocks a scikit-learn DLL) — same model runs via ONNX instead
- Knowledge base is a small sample company (Aurora Electronics)

## Future Improvements

- Memory and conversation persistence (V4)
- Web search, order lookup, CRM tools (V3, V7)
- Support tickets and settings pages (V6)
- Human-in-the-loop escalation (V9)
- Multi-agent workflows (V10)

See `CONSTITUTION.C.md` §27 for the full version roadmap.

## Project Docs

| File | Purpose |
|---|---|
| `CONSTITUTION.C.md` | rules the project follows |
| `skills.md` | agent capability catalog |
| `agents.md` | agent system definition |
| `spec/requirements.md` | functional/non-functional requirements, DoD |
| `spec/design.md` | architecture, module contracts |
| `spec/milestones.md` | build order (M1–M7) |
| `process.md` | session state and resume procedure |

## License

For portfolio and learning use.
