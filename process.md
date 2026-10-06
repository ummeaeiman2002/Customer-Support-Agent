# Process — Session Continuity & Work State

**Purpose:** If the terminal/session terminates, any developer or coding agent
can resume exactly where work stopped using this file alone.

**Rules on resume (§23):**
1. Read `CONSTITUTION.C.md` first.
2. Read this file's Current State and Log below.
3. Inspect the repository — trust the files, not the log, if they disagree.
4. Continue only the first unfinished item; do not skip milestones (§24).
5. Never regenerate finished work.

---

## 1. Current State

| Field | Value |
|---|---|
| Phase | Version 1 COMPLETE (M1–M7) |
| Next action | Optional: commit to git, portfolio polish, or V2 (§27) |
| Last updated | 2026-10-06 |
| Working tree | code + docs; git repo initialized (no commits yet) |
| Tests passing | 42/42 (`pytest`) |
| Live demo | `python -m customer_support_agent.server` → http://127.0.0.1:8000 |
| Blockers | none |

---

## 2. Decisions Locked In (M0)

Do not re-ask these:

| Decision | Choice |
|---|---|
| LLM API | Groq free tier — `openai/gpt-oss-120b` (OpenAI-compatible SDK) |
| Also supported | `openai` (paid) and `ollama` (local) via `LLM_PROVIDER` |
| Embeddings | local ONNX `all-MiniLM-L6-v2` (chromadb backend; sentence-transformers blocked by App Control policy on this machine) |
| Vector store | Chroma (local, persistent) |
| V1 interface | CLI + minimal stdlib localhost UI (`http.server`) |
| Structure | `src/customer_support_agent/` per constitution §18 |

---

## 3. File Inventory

| File | Status | Purpose |
|---|---|---|
| `CONSTITUTION.C.md` | done | Master rules — read always |
| `skills.md` | done | Agent capability catalog |
| `agents.md` | done | Agent system definition |
| `spec/requirements.md` | done | FR/NFR, DoD, acceptance scenarios |
| `spec/design.md` | done | Architecture, module contracts, config, errors |
| `spec/milestones.md` | done | M1–M7 build order |
| `process.md` | done | This file — resume point |
| `README.md` | done | Portfolio readme (§22) |
| `pyproject.toml` | done | Package + deps: openai, chromadb, pytest |
| `.gitignore` / `.env.example` | done | §10; `.env` verified git-ignored |
| `src/...` | done | agent, llm, rag, tools, config, utils |
| `knowledge/*.md` | done | Aurora Electronics sample docs (3 files, 6 chunks) |
| `tests/*.py` | done | 42 tests, all passing |
| git init | done | no commits made yet (needs your request) |
| `scripts/ingest.py` | done | repeatable ingestion |

---

## 4. Milestone Checklist (copy of spec/milestones.md status)

- [x] M0 — Decisions locked (table §2 above)
- [x] M1 — Project skeleton, settings, logging, first tests
- [x] M2 — LLM client + system instructions + state + CLI chat
- [x] M3 — Calculator tool + tool-call loop
- [x] M4 — knowledge/ docs + ingestion pipeline + `scripts/ingest.py`
- [x] M5 — Retrieval + grounding (acceptance A2/A3/A5 verified live)
- [x] M6 — Full error model + logging audit (A6/A7 covered by tests)
- [x] M7 — Full test suite (42) + README + DoD checklist (§26)

---

## 5. Resume Procedure (step by step)

```text
1. Open repo:   E:\Downloads\Customer-Support-Agent\Customer-support-Agent-Main
2. Read:        CONSTITUTION.C.md (always)
3. Read:        process.md §1–§4 (this file)
4. Find first unchecked box in §4 above
5. Read matching milestone in spec/milestones.md
6. Read spec/design.md sections needed for that milestone
7. Implement ONLY that milestone
8. Run:         pytest        (once code exists)
9. Fix failures before stopping
10. Update §1, §3, §4 of this file before ending the session
```

If code exists but state is unclear:

```text
pytest                 # are tests green?
python -m src.customer_support_agent.main   # does it start?
git status / git log   # what changed last?
```

---

## 6. Session Log

Append one line per session — newest last.

```text
2026-10-06 | docs    | Read constitution; created skills.md, agents.md, spec/*, process.md
2026-10-06 | M1-M3   | Skeleton + LLM client + CLI + calculator + stdlib localhost UI; 24 tests
2026-10-06 | provider | OpenAI 429 quota -> Ollama installed/pulled/tested -> uninstalled (user) -> Groq free tier (gpt-oss-120b, tool calling verified)
2026-10-06 | M4-M5   | knowledge/ docs, rag pipeline, search_knowledge tool, chromadb ONNX embeddings (sentence-transformers blocked by App Control); 42 tests; live acceptance passed
2026-10-06 | M6-M7   | docs synced to tool-based retrieval, README, secret-log audit, git init, DoD met; 42/42
```

---

## 7. Emergency Rules

- If a change conflicts with the constitution: stop, note it here, propose the
  smallest alternative before coding (§23).
- Never commit `.env` or log API keys (§10).
- Never mark a milestone checked without running its exit criteria.
- If lost: fall back to `spec/milestones.md` — it defines "done" for every step.
