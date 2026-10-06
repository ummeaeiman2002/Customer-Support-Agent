# Specification — Milestones

**Derived from:** `CONSTITUTION.C.md` (§23, §24, §26)
**Rule:** one milestone at a time; each leaves the project in a working state;
tests run after meaningful changes; fix errors before moving on.

Workflow per milestone: Understand → Design → Implement → Run → Test → Debug →
Refactor → Document.

---

## M0 — Decisions (done)

| Decision | Choice |
|---|---|
| LLM API | OpenAI (`gpt-4o-mini`) |
| Embeddings | `text-embedding-3-small` (1536-dim) |
| Vector store | Chroma (local, persistent) |
| UI (V1) | CLI |
| Docs | `CONSTITUTION.C.md`, `skills.md`, `agents.md`, `spec/*` |

---

## M1 — Project Skeleton

**Build:**
- `pyproject.toml`, `.gitignore`, `.env.example`, `README.md` stub
- `src/customer_support_agent/` package with `config/settings.py`, `utils/logging.py`
- Empty-but-importable `main.py` printing a greeting
- `tests/test_settings.py`, `tests/test_logging.py`

**Exit criteria:**
- Package imports cleanly; `load_settings()` reads env
- `.env` ignored by git; `.env.example` lists every key from design §5
- `pytest` passes; no secrets anywhere in tracked files

---

## M2 — LLM Client + Basic Conversation

**Build:**
- `llm/client.py` with error wrapping (design §6)
- `agent/prompts.py` (system instructions, no business facts)
- `agent/state.py`
- `agent/agent.py` minimal loop: user → LLM → text
- `main.py` CLI REPL (exit command, empty-input handling)

**Exit criteria:**
- Live conversation works with real API key
- Invalid key / timeout / rate limit produce friendly messages, no stack traces
- `tests/test_agent.py`: normal question (mocked LLM)

---

## M3 — Calculator Tool

**Build:**
- `tools/calculator.py` (`validate` + `evaluate`, ast-based safe eval)
- Tool schema + whitelist in agent; tool-call loop with argument validation
- Bounded iterations (`MAX_TOOL_ITERATIONS`)

**Exit criteria:**
- "What is 49 × 3?" → `147` via tool, not mental math
- Invalid expression → clean tool error, agent recovers
- `tests/test_tools.py`: valid, invalid, edge cases (§14) — all pass

---

## M4 — Knowledge Base + Ingestion

**Build:**
- `knowledge/company.md`, `knowledge/products.md`, `knowledge/refund-policy.md`
- `rag/ingestion.py` (load → clean → chunk), `rag/embeddings.py`,
  `rag/vector_store.py` (Chroma wrapper with `reset`)
- `scripts/ingest.py` CLI

**Exit criteria:**
- Re-running ingest is idempotent/repeatable (§6.1)
- `tests/test_rag.py`: ingestion works with mocked embeddings

---

## M5 — Retrieval + Grounding

**Build:**
- `rag/retriever.py` (`search`, `get_context` with relevance threshold)
- Agent integration: knowledge-needed path, `<knowledge>` block injection,
  per-turn context clearing
- Grounding rules in system instructions (§7)

**Exit criteria:**
- Acceptance scenarios A2, A3, A5 pass (requirements §5)
- Full knowledge base is never sent to the LLM
- `tests/test_agent.py`: knowledge question + unknown question (mocked)

---

## M6 — Error Handling + Logging Pass

**Build:**
- Full error model per design §6 (including Chroma failure → chat still works)
- Log events per §13; audit that no secrets are logged

**Exit criteria:**
- Scenarios A6, A7 pass
- Manual fault injection (bad key, deleted chroma dir) → graceful behavior

---

## M7 — Tests + README + DoD

**Build:**
- Complete `tests/` per §14 (agent: normal/knowledge/tool/unknown; RAG: ingest/
  retrieve/relevant/irrelevant/empty; tools: valid/invalid/edge) with mocks
- `README.md`: overview, problem, features, architecture, workflow, RAG pipeline,
  tool calling, tech stack, example conversations, install, env vars, testing,
  limitations, future improvements (§22 — honest, no fake metrics)
- Tick every box in requirements §4 (DoD)

**Exit criteria:**
- All tests pass locally; project demoable end-to-end
- DoD checklist fully checked
- Git history clean; `.env` never committed

---

## Milestone Rules (§23–§24)

1. No starting M(n+1) with failing tests or known errors from M(n).
2. Changes stay focused on the current milestone.
3. If a change conflicts with the constitution: identify → explain → propose the
   smallest alternative → never silently violate.
4. Do not generate the entire application in one step.

## Future (after V1, §27)

V2 better tool system → V3 web search → V4 memory → V5 FastAPI →
V6 auth → V7 DB/CRM → V8 n8n → V9 human-in-the-loop → V10 multi-agent.
Each only when an actual requirement justifies it.
