# AI Customer Support & Knowledge Agent — Agent Definition

**Derived from:** `CONSTITUTION.C.md`
**Companion docs:** `skills.md` (capability catalog)

This document defines the agent itself: its components, orchestration loop,
state, prompts, and boundaries. It is business-independent — swapping the
business swaps `knowledge/` and instructions, not this architecture (§21).

---

## 1. What This System Is (§3)

An AI agent, not a chatbot. Four components:

```text
┌─────────────────────────────────────────────┐
│                  AGENT                      │
│                                             │
│  LLM ────────── language understanding,     │
│                 reasoning, response         │
│                 generation                  │
│                                             │
│  Instructions ─ role, behavior, limits,     │
│                 grounding + safety rules    │
│                                             │
│  Knowledge ──── RAG retrieval from          │
│                 authoritative documents     │
│                                             │
│  Tools ──────── deterministic actions       │
│                 (v1: calculator)            │
└─────────────────────────────────────────────┘
```

Responsibilities never blur (§17):
- The LLM decides; it never executes anything directly.
- Knowledge retrieval returns documents; it never decides or answers.
- Tools execute validated inputs; they never orchestrate.
- Instructions define behavior; they never contain business facts.

---

## 2. Components and Files (§17)

```text
src/customer_support_agent/
├── agent/
│   ├── agent.py       # orchestration loop: decide → act → respond
│   ├── prompts.py     # SYSTEM_INSTRUCTIONS template + context injection
│   └── state.py       # conversation state (messages, turn metadata)
├── llm/
│   └── client.py      # OpenAI API wrapper: chat + tool-calling, error handling
├── rag/
│   ├── ingestion.py   # load → clean → chunk
│   ├── embeddings.py  # text-embedding-3-small wrapper
│   ├── vector_store.py# Chroma persistence
│   └── retriever.py   # top-k similarity search → context
├── tools/
│   └── calculator.py  # validate → execute → result
├── config/
│   └── settings.py    # model names, k, paths, log level (from env)
└── utils/
    └── logging.py     # structured events, never secrets
```

Data flow between components:

```text
main.py
  → agent.run(user_message, state)
      → llm.client.chat(messages, tools)
          ⇄ rag.retriever.search(query)        (via search_knowledge tool)
          ⇄ tools.calculator.evaluate(expr)    (if tool needed)
      → final text
  → state updated → stdout
```

---

## 3. Orchestration Loop (§4, §9)

```text
1. Receive user message
2. Update state (append user message)
3. Call LLM with: system instructions + message history
                  + tool definitions + (context if retrieval active)
4. LLM responds with one of:
   a. Tool call(s)   → validate arguments → execute → append result
                       → return to step 3
   b. search_knowledge call → embed query → vector search (score ≥ threshold)
                       → formatted chunks as tool result → return to step 3
   c. Final text     → append assistant message → return to caller
5. Bounded: max iterations per turn (prevents infinite tool loops)
```

Rules:
- Never call every tool or retrieve blindly (§4) — retrieval happens only
  when the LLM decides company knowledge is needed.
- Never execute unvalidated LLM output (§9) — arguments pass a validator first.
- Only whitelisted tools are callable; the LLM cannot invent functions (§8).
- Every loop iteration is logged: tool requested → tool executed → response (§13).

---

## 4. State (`agent/state.py`)

Minimal, explicit, no framework:

```text
ConversationState
├── messages: list[dict]     # role/content/tool_call entries, in order
├── retrieved_context: str   # chunks injected for the current turn (reset each turn)
├── turn_count: int
└── metadata: dict           # e.g. tools_used, retrieval_performed
```

- No long-term memory in Version 1 (§20).
- `retrieved_context` is per-turn: stale knowledge must not leak into later turns.
- State is data only — no behavior, no LLM calls inside it.

---

## 5. System Instructions (`agent/prompts.py`)

Instructions define role, behavior, limitations, grounding, and safety (§3).
Stored as a template string, not as code logic:

```text
Role:        customer support assistant for a configured company
Behavior:    conversational, concise, one skill per request
Grounding:   company facts ONLY from provided context; if absent →
             "I couldn't find that information in the available company
             knowledge base." (§7)
Tools:       use calculator for arithmetic; never mental math when available (§8)
Safety:      no fabricated prices/policies/guarantees; no secrets; no
             stack traces (§7, §10, §12)
Limitations: no web access, no order lookup, no email (§20)
```

Rules:
- Instructions never contain business facts (prices, policies) — those come
  from `knowledge/` via the `search_knowledge` tool (§5, §21).
- The instruction text is swappable per business; the agent core is not
  rewritten (§21: Reusable Agent Core + Business Knowledge + Business Tools).
- Retrieved chunks reach the LLM as tool results (role `tool`), clearly
  labeled with their source file, never mixed into user messages.

---

## 6. LLM Client (`llm/client.py`)

- OpenAI chat completions; model from settings (§11).
- Accepts: message list + tool schemas; returns: text or tool calls.
- Never contains customer-specific policies (§17).
- Error handling (§12): invalid API key, timeout, rate limit, malformed
  response → typed exceptions or clean fallback message; never leak internals.

---

## 7. Knowledge Path (§5, §6)

Ingestion (offline, repeatable — `scripts/ingest.py`):

```text
knowledge/*.md → load → clean → chunk → embed → Chroma
```

Retrieval (per turn, only when the LLM asks for it):

```text
search_knowledge(query) → embed → top-k vector search → score filter
  → chunks with source refs as tool result → LLM
```

- Never send the whole knowledge base to the LLM (§6.2).
- Threshold: chunks below `RETRIEVAL_MIN_SCORE` are dropped; an empty
  result forces the honest-limitation reply (§7).
- If the vector store is unavailable, the tool is not offered and company
  questions fall through to the honest-limitation reply (§12).

---

## 8. Tool Path (§8, §9)

```text
tool schema (name, params) declared to LLM
   ↓
LLM emits tool call
   ↓
validate(args) → CalculatorError on bad input
   ↓
execute in isolation (pure function, no I/O)
   ↓
result (or error string) back to LLM
```

- Clearly named, isolated, independently testable, deterministic (§8).
- v1 whitelist: `calculator` only. New tools follow the same pattern (§27).

---

## 9. Configuration (§11) and Secrets (§10)

`config/settings.py` reads environment variables once:

```text
LLM_MODEL, EMBEDDING_MODEL, LLM_API_KEY
CHROMA_PATH, KNOWLEDGE_DIR
RETRIEVAL_TOP_K, LOG_LEVEL, MAX_TOOL_ITERATIONS
```

- `.env` holds secrets; `.env.example` documents them; `.env` git-ignored.
- No configuration values scattered through the codebase.
- Never logged: API keys, tokens, passwords (§10, §13).

---

## 10. Logging (§13) and Errors (§12)

Logged events: request received → LLM request started/completed →
knowledge search started/completed → tool requested/executed →
final response generated → error occurred.

Error handling covers: bad API key, timeout, rate limit, malformed response,
vector DB failure, invalid tool args, missing knowledge, empty message.
User-facing messages stay understandable; stack traces stay in logs (§12).

---

## 11. Reusability Contract (§21)

```text
Reusable Agent Core  +  Business Knowledge  +  Business Tools  =  Agent
(architecture above)    (knowledge/*.md,         (tools/*.py,
                         instructions template)    versioned per business)
```

Changing the business = replace `knowledge/`, adjust the instructions
template, add business tools. `agent/`, `llm/`, `rag/` core stay untouched.

---

## 12. Related Rules

- Capability behaviors, triggers, examples, and tests: `skills.md`
- Build order and milestones: constitution §23–§24
- Version 1 scope: constitution §20
