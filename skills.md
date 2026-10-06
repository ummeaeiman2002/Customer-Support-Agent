# AI Customer Support & Knowledge Agent — Skills Catalog

**Derived from:** `CONSTITUTION.C.md`
**Scope:** Version 1 (§20)

A skill is a defined capability of the agent: what triggers it, what data it uses,
what it may and may not do, and how it is tested.

Skills are business-independent. Company facts live in `knowledge/`, never inside
skill logic (§5, §21).

---

## Skill Selection Rules

The LLM chooses exactly one skill path per user request (§4):

```text
User Request
   ↓
Is it a calculation / numeric operation?  → Skill 3: Calculator
Does it need company-specific facts?      → Skill 2: Knowledge Answer
Otherwise                                  → Skill 1: General Conversation
Information required but unavailable?     → Skill 4: Honest Limitation
```

Rules:
- Do not call tools or retrieve knowledge when they are not needed (§4).
- Never run two skill paths for one request unless the request genuinely contains
  two parts (e.g. "What's the refund window, and what's 10% of 250?").
- Tool execution requires argument validation before running (§9).

---

## Skill 1 — General Conversation

| Field | Value |
|---|---|
| Purpose | Understand and answer ordinary non-company questions conversationally (§1, §3) |
| Trigger | Greetings, small talk, general knowledge, clarifying questions about the agent itself |
| Knowledge required | No |
| Tools required | No |

### Flow

```text
User message → LLM with system instructions → response
```

### Rules

- Stay in the agent role defined by system instructions (§3).
- No company-specific claims of any kind — prices, policies, delivery times (§7).
- Never expose stack traces, secrets, or internal details (§12).
- Empty user message → friendly request to rephrase, not an error (§12).

### Example

```text
User: Hi, are you a bot?
Agent: I'm an AI customer support assistant. I can answer questions about the
       company's products and policies, and help with calculations. What can
       I help you with?
```

### Tests

- Normal greeting returns a role-consistent reply.
- Empty message handled gracefully.

---

## Skill 2 — Knowledge Answer (RAG)

| Field | Value |
|---|---|
| Purpose | Retrieve and use authoritative company information (§1, §5) |
| Trigger | Questions about products, policies, refunds, prices, delivery, company facts |
| Knowledge required | Yes — `knowledge/` documents |
| Tools required | `search_knowledge` (retrieval is a tool, not a blind step) |

### Flow (§6.2)

```text
User question
   ↓
LLM decides company knowledge is needed (§4 — never retrieves blindly)
   ↓
LLM calls search_knowledge(query)
   ↓
Embed query (same embedding model as ingestion)
   ↓
Vector search in Chroma (top-k chunks, score ≥ RETRIEVAL_MIN_SCORE)
   ↓
Relevant chunks formatted with source refs → tool result
   ↓
LLM with system instructions + tool result
   ↓
Grounded answer, or the honest-limitation reply (Skill 4)
```

### Rules

- Answer ONLY from `search_knowledge` results. Never invent prices, policies,
  specifications, guarantees, delivery times, or legal claims (§7).
- Never send the entire knowledge base to the LLM — tool results only (§6.2).
- If the tool returns no relevant chunks (score below
  `RETRIEVAL_MIN_SCORE`) → Skill 4.
- Ingestion must be repeatable: load → clean → chunk → embed → store (§6.1).
- Business content lives in `knowledge/*.md`, never in Python source (§5).
- If the vector store is unavailable, the tool is not offered; company
  questions fall through to Skill 4 (§12).

### Example

```text
User: What's your refund window?
Agent → tool call: search_knowledge("refund window")
Agent → tool result: [refund-policy.md] Refunds within 30 days of delivery...
Agent: You can request a refund within 30 days of delivery, as long as the
       item is unused and in its original packaging.
```

### Tests (§14)

- Ingestion of sample documents succeeds and is repeatable.
- Relevant query returns relevant chunk.
- Irrelevant query returns no meaningful chunk.
- Empty query handled without crash.

---

## Skill 3 — Calculator Tool

| Field | Value |
|---|---|
| Purpose | Deterministic numeric operations instead of mental arithmetic (§8) |
| Trigger | Explicit math requests: totals, percentages, quantities |
| Knowledge required | No |
| Tools required | `calculator` |

### Flow (§9)

```text
User request
   ↓
LLM determines a tool is necessary
   ↓
Validate arguments (expression must be safe, parseable)
   ↓
Execute calculator in isolation
   ↓
Return result to LLM
   ↓
LLM formats final response
```

### Rules

- The calculator is isolated from the LLM, clearly named, independently
  testable, and deterministic (§8).
- Never blindly execute arbitrary functions from unvalidated LLM output (§9).
- Only the whitelisted `calculator` tool may be executed in Version 1 (§20).
- If arguments are invalid → return a clear tool error, never execute.

### Example

```text
User: What is 49 × 3?
Agent → tool call: calculator("49 * 3")
Agent → user: The total is 147.
```

### Tests (§14)

- Valid input → correct result (`49 * 3 = 147`).
- Invalid input (e.g. `abc`, `1 / 0`) → clean error, no exception leak.
- Edge cases: decimals, negatives, large numbers.

---

## Skill 4 — Honest Limitation

| Field | Value |
|---|---|
| Purpose | State clearly when required information is unavailable (§1, §7) |
| Trigger | No relevant chunk retrieved, or question outside the knowledge base |
| Knowledge required | Attempted, empty |
| Tools required | No |

### Rules

- Preferred response (verbatim, §7):

  > "I couldn't find that information in the available company knowledge base."

- Never fabricate information merely to appear helpful (§7).
- Never guess a price, policy, or date "probably".
- Optionally suggest contacting human support if configured in knowledge docs.

### Example

```text
User: Do you ship to Antarctica?
Agent: I couldn't find that information in the available company knowledge base.
       Would you like me to help with anything else?
```

### Tests

- Query with no matching knowledge → refusal phrase used.
- Agent never outputs a company fact when retrieval is empty.

---

## Skill Boundaries (§17)

```text
agent/    → decides which skill runs, builds context, formats final answer
llm/      → sends messages, returns responses; holds no policies
rag/      → ingestion + retrieval only; no UI or orchestration logic
tools/    → calculator only; no agent orchestration
config/   → settings only; no business logic
knowledge/→ all company facts; never hard-coded in Python
```

## Version 1 Out of Scope (§20)

No web search, database lookup, email, CRM, calendar, order lookup, or external
API skills. Future skills must follow this same template: trigger, flow, rules,
example, tests.
