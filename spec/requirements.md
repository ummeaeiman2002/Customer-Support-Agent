# Specification — Requirements

**Derived from:** `CONSTITUTION.C.md` (§20, §26)
**Status:** Version 1

---

## 1. Functional Requirements

### FR-1 — Conversation
- The agent accepts user text input and returns a text response (CLI).
- System instructions define role, behavior, limitations, grounding, and safety (§3).
- Empty or whitespace-only input is handled gracefully (§12).

### FR-2 — Knowledge Answers (RAG)
- Company knowledge lives in `knowledge/*.md`, never in Python (§5).
- Documents can be ingested repeatably: load → clean → chunk → embed → store (§6.1).
- At runtime, only relevant retrieved chunks are sent to the LLM — never the full
  knowledge base (§6.2).
- Retrieval with no relevant match results in the honest-limitation response.

### FR-3 — Tools
- Version 1 provides exactly one tool: `calculator` (§8).
- Tool arguments are validated before execution; invalid input returns a clean
  error, never an exception leak (§9, §12).
- The agent uses the calculator for arithmetic instead of mental math when the
  tool is available (§8).

### FR-4 — Grounding
- Company-specific answers are grounded exclusively in retrieved context (§7).
- The agent never invents prices, policies, specifications, refund rules,
  guarantees, delivery times, company facts, or legal claims (§7).
- When information is unavailable, the agent states:

  > "I couldn't find that information in the available company knowledge base."

### FR-5 — Skill Selection
- One skill path per request: calculator / knowledge / general conversation /
  honest limitation (see `skills.md`).
- No blind tool calls and no unnecessary retrieval (§4).

---

## 2. Non-Functional Requirements

| ID | Requirement | Constitution |
|---|---|---|
| NFR-1 | Understandable, explicit Python; small modules; no premature abstraction | §2.1 |
| NFR-2 | No frameworks (LangChain/LangGraph/CrewAI) in V1 | §2.2, §16 |
| NFR-3 | Secrets only via `.env`; `.env.example` provided; `.env` git-ignored | §10 |
| NFR-4 | No secrets or sensitive data ever logged | §10, §13 |
| NFR-5 | Configuration centralized in `config/settings.py`, sourced from env vars | §11 |
| NFR-6 | Errors handled: bad key, timeout, rate limit, malformed response, vector DB failure, invalid tool args, missing knowledge, empty message | §12 |
| NFR-7 | User-facing errors understandable; no stack traces or internals exposed | §12 |
| NFR-8 | Key events logged: request, LLM call, knowledge search, tool call, response, error | §13 |
| NFR-9 | Agent, RAG, and tools independently testable; tests mock live APIs | §14 |
| NFR-10 | Type hints where useful, small functions, no giant files or dead code | §15 |
| NFR-11 | Minimal dependency set, each dependency justified | §16 |
| NFR-12 | Clear module boundaries: RAG ≠ UI, tools ≠ orchestration, config ≠ business logic | §17 |
| NFR-13 | Business facts swappable without rewriting the agent core | §21 |
| NFR-14 | Honest portfolio presentation; no claimed deployments/metrics that don't exist | §22 |

---

## 3. Version 1 Scope (§20)

**In scope:** Python · LLM API (OpenAI) · system instructions · basic conversation ·
knowledge documents · RAG (Chroma + text-embedding-3-small) · vector storage ·
calculator tool · basic orchestration · error handling · logging · tests ·
README · environment configuration · CLI.

**Out of scope:** multi-agent systems · voice · authentication · payments ·
cloud deployment · frontend · CRM/email · advanced memory · background tasks ·
Kubernetes · observability platforms.

---

## 4. Definition of Done — Version 1 (§26)

- [ ] Project structure is clean
- [ ] LLM integration works
- [ ] Environment variables configured safely
- [ ] User can ask questions
- [ ] Agent can answer normal questions
- [ ] Knowledge documents can be ingested
- [ ] RAG retrieval works
- [ ] Agent can use retrieved knowledge
- [ ] Agent can use the calculator tool
- [ ] Agent does not invent unavailable company information
- [ ] Errors are handled
- [ ] Tests exist and pass
- [ ] README explains the architecture
- [ ] `.env` excluded from Git
- [ ] `.env.example` exists
- [ ] Code is understandable
- [ ] Project can be demonstrated locally

---

## 5. Acceptance Scenarios

| # | Scenario | Expected |
|---|---|---|
| A1 | "Hi" | Conversational reply in agent role |
| A2 | "What's your refund window?" (knowledge exists) | Grounded answer from retrieved chunk |
| A3 | "Do you ship to Antarctica?" (no knowledge) | Honest-limitation sentence |
| A4 | "What is 49 × 3?" | `147`, computed via calculator tool |
| A5 | "What's the price of X?" (never documented) | Refusal — no invented price |
| A6 | API key invalid | Friendly error message, no stack trace, no key in logs |
| A7 | Empty input | Prompt to rephrase, no crash |
