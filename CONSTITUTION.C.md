# AI Customer Support & Knowledge Agent — Constitution

## 1. Project Identity

**Project:** AI Customer Support & Knowledge Agent

**Purpose:** Build a reusable, portfolio-quality AI agent that can:
- Understand customer questions.
- Answer general questions conversationally.
- Retrieve authoritative company information using RAG.
- Use tools when appropriate.
- Avoid fabricating company-specific information.
- Clearly state when required information is unavailable.
- Be easy to customize for future businesses and Upwork projects.

This project is both a learning project and a reusable foundation for future AI automation work.

---

## 2. Core Principles

### 2.1 Understandability Over Abstraction

Code must be understandable to a developer learning agentic AI.

Prefer:
- Simple Python.
- Explicit functions.
- Clear naming.
- Small modules.
- Readable control flow.

Avoid unnecessary:
- Complex design patterns.
- Excessive abstraction.
- Deep inheritance.
- Premature optimization.
- Large frameworks without a clear reason.

Every abstraction must solve a real problem.

### 2.2 Fundamentals First

Important AI concepts must not be hidden behind frameworks.

The developer should understand:
- LLM requests and responses.
- System and user messages.
- Tool calling.
- Tool results.
- Embeddings.
- Retrieval.
- Context construction.
- Final response generation.

Frameworks such as LangChain, LangGraph, or CrewAI may be introduced later only when they provide clear value.

### 2.3 Reusability

Business-specific information must not be hard-coded into application logic.

The same agent core should eventually work with different:
- Knowledge bases.
- System instructions.
- Tools.
- Business configurations.

---

## 3. Agent Definition

The system is an AI agent, not merely a chatbot.

The agent consists of:

### LLM
Responsible for:
- Understanding language.
- Reasoning about requests.
- Deciding whether tools or knowledge are needed.
- Generating responses.

### Instructions
Define:
- Agent role.
- Behavior.
- Limitations.
- Grounding rules.
- Safety rules.

### Knowledge Retrieval
Allows the agent to retrieve relevant information from authoritative documents.

### Tools
Allow the agent to perform deterministic actions or calculations.

Version 1 requires:
- Calculator tool.

Future tools may include:
- Web search.
- Database lookup.
- Email.
- CRM.
- Calendar.
- Order lookup.
- External APIs.

---

## 4. Runtime Workflow

The conceptual runtime flow is:

```text
User
  ↓
Application
  ↓
Agent
  ↓
LLM
  ↓
Determine intent / required action
  ↓
┌─────────────────────────────┐
│ Knowledge required? → RAG   │
│ Tool required?      → Tool  │
└─────────────────────────────┘
  ↓
Results / Context
  ↓
LLM
  ↓
Final Response
  ↓
User
```

The agent must not blindly call every tool or retrieve unnecessary information.

---

## 5. Knowledge Base

Company-specific knowledge must be stored separately from application code.

Recommended structure:

```text
knowledge/
├── company.md
├── products.md
└── refund-policy.md
```

Business policies and facts belong in the knowledge base, not inside Python source code.

---

## 6. RAG Pipeline

### 6.1 Ingestion

```text
Documents
   ↓
Load
   ↓
Clean
   ↓
Chunk
   ↓
Generate Embeddings
   ↓
Store in Vector Database
```

The ingestion process must be repeatable.

### 6.2 Runtime Retrieval

```text
User Question
   ↓
Question Embedding
   ↓
Vector Search
   ↓
Relevant Chunks
   ↓
Context
   ↓
LLM
   ↓
Grounded Answer
```

Do not send the entire knowledge base to the LLM.

---

## 7. Grounding Rules

Company-specific answers must be grounded in retrieved knowledge.

The agent must not invent:
- Prices.
- Policies.
- Product specifications.
- Refund rules.
- Guarantees.
- Delivery times.
- Company facts.
- Legal claims.

If required information is unavailable, say so clearly.

Preferred response:

> "I couldn't find that information in the available company knowledge base."

Do not fabricate information merely to appear helpful.

---

## 8. Tool Rules

Tools must be:
- Clearly named.
- Isolated from the LLM.
- Independently testable.
- Validated before execution.
- Deterministic where practical.

Version 1 includes:

```text
calculator
```

Example:

```text
User: What is 49 × 3?
Agent → Calculator → 147
Agent → User: The total is 147.
```

The LLM should use the calculator instead of relying on mental arithmetic when a calculator tool is available.

---

## 9. Tool Calling

Tool execution must follow:

```text
User Request
    ↓
LLM determines tool is necessary
    ↓
Validate tool arguments
    ↓
Execute tool
    ↓
Return tool result
    ↓
LLM generates response
```

Never blindly execute arbitrary functions from unvalidated LLM output.

---

## 10. Security

Secrets must never be hard-coded.

Never commit API keys.

Use environment variables:

```text
.env
```

and provide:

```text
.env.example
```

Example:

```text
LLM_API_KEY=your_api_key_here
```

The `.env` file must be excluded from Git.

Never log:
- API keys.
- Passwords.
- Access tokens.
- Private credentials.
- Sensitive user information.

---

## 11. Configuration

Keep configuration separate from business logic.

Configuration may include:
- Model name.
- API settings.
- Vector database settings.
- Retrieval parameters.
- Logging level.
- Environment.

Do not scatter configuration values throughout the codebase.

---

## 12. Error Handling

Gracefully handle:
- Invalid API keys.
- API timeouts.
- Rate limits.
- Malformed responses.
- Vector database failures.
- Invalid tool arguments.
- Missing knowledge.
- Empty user messages.

User-facing errors must be understandable.

Do not expose stack traces, secrets, or internal implementation details to end users.

---

## 13. Logging

Logs should help developers understand system behavior.

Useful events:
- Agent request received.
- LLM request started/completed.
- Knowledge search started/completed.
- Tool call requested.
- Tool executed.
- Final response generated.
- Error occurred.

Never log secrets or sensitive data.

---

## 14. Testing

Important components must be independently testable.

### Agent
Test:
- Normal question.
- Knowledge question.
- Tool question.
- Unknown question.

### RAG
Test:
- Document ingestion.
- Retrieval.
- Relevant result.
- Irrelevant result.
- Empty query.

### Tools
Test:
- Valid calculator input.
- Invalid input.
- Edge cases.

Avoid unnecessary dependence on live external APIs in tests. Use mocks where appropriate.

---

## 15. Code Quality

Use:
- Descriptive names.
- Small functions.
- Type hints where useful.
- Docstrings for non-obvious behavior.
- Consistent formatting.
- Clear module boundaries.

Avoid:
- Giant files.
- Giant functions.
- Duplicated code.
- Magic numbers.
- Dead/commented-out code.
- Unnecessary comments.

---

## 16. Dependency Rules

Use the smallest reasonable dependency set.

Before adding a package, ask:
1. Is it actually needed?
2. Can the standard library solve this simply?
3. Does it improve maintainability?
4. Is it actively maintained?
5. Does it introduce unnecessary complexity?

Do not install frameworks simply because they are popular.

---

## 17. Architecture

Maintain clear boundaries:

```text
src/customer_support_agent/
├── agent/
│   ├── agent.py
│   ├── prompts.py
│   └── state.py
├── llm/
│   └── client.py
├── rag/
│   ├── ingestion.py
│   ├── embeddings.py
│   ├── retriever.py
│   └── vector_store.py
├── tools/
│   └── calculator.py
├── config/
│   └── settings.py
└── utils/
    └── logging.py
```

Responsibilities must remain separated:
- RAG does not contain UI logic.
- Tools do not contain agent orchestration.
- Configuration does not contain business logic.
- LLM clients do not contain customer-specific policies.

---

## 18. Recommended Project Structure

```text
customer-support-agent/
├── CONSTITUTION.md
├── README.md
├── .env.example
├── .gitignore
├── pyproject.toml
│
├── src/
│   └── customer_support_agent/
│       ├── __init__.py
│       ├── main.py
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── prompts.py
│       │   └── state.py
│       ├── llm/
│       │   ├── __init__.py
│       │   └── client.py
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── ingestion.py
│       │   ├── embeddings.py
│       │   ├── retriever.py
│       │   └── vector_store.py
│       ├── tools/
│       │   ├── __init__.py
│       │   └── calculator.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       └── utils/
│           ├── __init__.py
│           └── logging.py
│
├── knowledge/
│   ├── company.md
│   ├── products.md
│   └── refund-policy.md
│
├── tests/
│   ├── test_agent.py
│   ├── test_rag.py
│   └── test_tools.py
│
└── scripts/
    └── ingest.py
```

The exact structure may be simplified during the first implementation if a file is not yet needed. Do not create empty modules solely to match the diagram.

---

## 19. API and UI

The initial version may be a CLI application.

Do not build a complicated frontend during Version 1.

The architecture should allow a future FastAPI layer.

Priority:

```text
Correct agent behavior
        >
Clean architecture
        >
Tests
        >
API
        >
UI
```

---

## 20. Version 1 Scope

Required:
- Python.
- LLM API.
- System instructions.
- Basic conversation.
- Knowledge documents.
- RAG.
- Vector storage.
- Calculator tool.
- Basic agent orchestration.
- Error handling.
- Logging.
- Tests.
- README.
- Environment configuration.

Not required:
- Multi-agent systems.
- Voice.
- Authentication.
- Payments.
- Cloud deployment.
- Complex frontend.
- CRM integration.
- Email integration.
- Advanced memory.
- Background autonomous tasks.
- Kubernetes.
- Complex observability platforms.

Keep Version 1 intentionally small.

---

## 21. Reusability

The project should eventually support:

```text
Reusable Agent Core
        +
Business Knowledge
        +
Business Tools
        =
Customized AI Agent
```

Changing the business should not require rewriting the core agent.

---

## 22. Portfolio Standards

The project must be honestly presentable as a professional portfolio project.

README should eventually contain:
- Project overview.
- Problem being solved.
- Features.
- Architecture.
- Workflow.
- RAG pipeline.
- Tool calling.
- Tech stack.
- Example conversations.
- Installation.
- Environment variables.
- Testing instructions.
- Limitations.
- Future improvements.

Never claim:
- Production deployment when none exists.
- Client usage when none exists.
- User numbers that were not measured.
- Performance metrics that were not measured.
- Technologies that were not actually used.

---

## 23. OpenCode Rules

OpenCode is an implementation assistant, not the project architect.

Before coding:
1. Read `CONSTITUTION.md`.
2. Inspect the repository.
3. Understand the current state.
4. Propose a plan.
5. Identify the first milestone.
6. Do not implement the entire system blindly.

During coding:
- Implement one milestone at a time.
- Keep changes focused.
- Run tests after meaningful changes.
- Fix errors before moving on.

If generated code is unclear, explain:
- What it does.
- Why it exists.
- What data flows through it.
- What assumptions it makes.

If a requested change conflicts with this constitution:
1. Identify the conflict.
2. Explain it.
3. Propose the smallest reasonable alternative.
4. Do not silently violate the constitution.

---

## 24. Development Workflow

Use:

```text
Understand
   ↓
Design
   ↓
Implement
   ↓
Run
   ↓
Test
   ↓
Debug
   ↓
Refactor
   ↓
Document
```

Each milestone must leave the project in a working state.

Do not generate the entire application in one step.

---

## 25. Learning Requirement

The developer must understand each major component before moving to the next stage.

Minimum understanding:

### LLM
- Request.
- Messages.
- Model.
- Response.
- Tokens at a high level.

### RAG
- Document.
- Chunk.
- Embedding.
- Vector.
- Similarity search.
- Retrieved context.

### Agent
- Instructions.
- Decision.
- Tool call.
- Tool result.
- Final response.

### Tool
- Input.
- Validation.
- Execution.
- Result.

The goal is not merely to make the application run.

The goal is to understand why it works.

---

## 26. Definition of Done — Version 1

Version 1 is complete when:

- [ ] Project structure is clean.
- [ ] LLM integration works.
- [ ] Environment variables are configured safely.
- [ ] User can ask questions.
- [ ] Agent can answer normal questions.
- [ ] Knowledge documents can be ingested.
- [ ] RAG retrieval works.
- [ ] Agent can use retrieved knowledge.
- [ ] Agent can use the calculator tool.
- [ ] Agent does not invent unavailable company information.
- [ ] Errors are handled.
- [ ] Tests exist and pass.
- [ ] README explains the architecture.
- [ ] `.env` is excluded from Git.
- [ ] `.env.example` exists.
- [ ] Code is understandable.
- [ ] Project can be demonstrated locally.

---

## 27. Future Evolution

Possible future versions:

```text
Version 1
LLM + RAG + Calculator
        ↓
Version 2
Better Tool System
        ↓
Version 3
Web Search
        ↓
Version 4
Memory
        ↓
Version 5
FastAPI
        ↓
Version 6
Authentication
        ↓
Version 7
Database / CRM
        ↓
Version 8
n8n Automation
        ↓
Version 9
Human-in-the-loop
        ↓
Version 10
Multi-Agent Workflows
```

Each evolution must be justified by an actual requirement.

---

## 28. Final Principle

Build something simple enough to understand today, but structured well enough to become valuable tomorrow.

The objective is not to demonstrate how many AI technologies can be used.

The objective is to demonstrate that the developer can:

> Design, build, understand, test, and extend a reliable AI agent that uses LLMs, knowledge retrieval, and tools to solve a real business problem.

When in doubt:

```text
Understandability
      ↓
Correctness
      ↓
Reliability
      ↓
Reusability
      ↓
Maintainability
      ↓
Complexity
```

Complexity must always be justified by value.
