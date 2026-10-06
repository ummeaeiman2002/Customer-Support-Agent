from __future__ import annotations

import json
import logging
from typing import Callable

from .prompts import SYSTEM_INSTRUCTIONS, build_messages
from .state import ConversationState
from ..llm.client import LLMClient, LLMError, ToolCall
from ..rag.retriever import Retriever
from ..tools.calculator import CALCULATOR_TOOL_SCHEMA, CalculatorError, evaluate

logger = logging.getLogger(__name__)

ToolFunc = Callable[[dict], str]

KNOWLEDGE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": (
            "Search the official company knowledge base. Always use this "
            "before answering any company-specific question."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Short search query, e.g. 'refund window'.",
                }
            },
            "required": ["query"],
        },
    },
}

TOOL_SCHEMAS_BY_NAME = {
    "calculator": CALCULATOR_TOOL_SCHEMA,
    "search_knowledge": KNOWLEDGE_TOOL_SCHEMA,
}

MAX_HISTORY_MESSAGES = 20
MAX_TOOL_RESULT_CHARS = 2000

FALLBACK_RESPONSE = (
    "Sorry, something went wrong on my side. Please try again in a moment."
)


def _run_calculator(arguments: dict) -> str:
    expression = arguments.get("expression")
    if not isinstance(expression, str):
        return "Error: missing or invalid 'expression' argument."
    try:
        return evaluate(expression)
    except CalculatorError as exc:
        return f"Error: {exc}"


def _make_knowledge_tool(retriever: Retriever) -> ToolFunc:
    def handler(arguments: dict) -> str:
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            return "Error: missing or invalid 'query' argument."
        chunks = retriever.search(query)
        return retriever.format_context(chunks)

    return handler


def build_tools(
    retriever: Retriever | None = None,
) -> dict[str, ToolFunc]:
    tools: dict[str, ToolFunc] = {"calculator": _run_calculator}
    if retriever is not None:
        tools["search_knowledge"] = _make_knowledge_tool(retriever)
    return tools


class SupportAgent:
    def __init__(
        self,
        llm: LLMClient,
        settings,
        tools: dict[str, ToolFunc] | None = None,
        system_instructions: str = SYSTEM_INSTRUCTIONS,
    ) -> None:
        self._llm = llm
        self._settings = settings
        self._tools = tools if tools is not None else build_tools()
        self._system = system_instructions
        self._schemas = [
            TOOL_SCHEMAS_BY_NAME[name]
            for name in self._tools
            if name in TOOL_SCHEMAS_BY_NAME
        ]

    def _execute_tool(self, call: ToolCall) -> str:
        logger.info("tool_call_requested name=%s", call.name)
        handler = self._tools.get(call.name)
        if handler is None:
            return f"Error: unknown tool '{call.name}'."
        if call.arguments.get("__invalid__") is not None:
            return "Error: tool arguments were not valid JSON."
        try:
            result = handler(call.arguments)
        except Exception:
            logger.exception("tool_execution_failed name=%s", call.name)
            return "Error: the tool failed to run."
        result = result[:MAX_TOOL_RESULT_CHARS]
        logger.info("tool_executed name=%s result_length=%d", call.name, len(result))
        return result

    def _to_raw_tool_calls(self, calls: list[ToolCall]) -> list[dict]:
        return [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.name,
                    "arguments": json.dumps(call.arguments),
                },
            }
            for call in calls
        ]

    def run(self, user_text: str, state: ConversationState | None = None) -> str:
        state = state or ConversationState()
        state.add_user(user_text)

        try:
            for _ in range(self._settings.max_tool_iterations):
                messages = build_messages(self._system, state.messages)
                response = self._llm.chat(messages, tools=self._schemas)

                if response.tool_calls:
                    state.add_assistant_tool_calls(
                        self._to_raw_tool_calls(response.tool_calls)
                    )
                    for call in response.tool_calls:
                        result = self._execute_tool(call)
                        state.add_tool_result(call.id, result)
                    continue

                text = response.text or FALLBACK_RESPONSE
                state.add_assistant(text)
                state.truncate_history(MAX_HISTORY_MESSAGES)
                logger.info("final_response length=%d", len(text))
                return text

            fallback = "I wasn't able to finish that request. Please try again."
            state.add_assistant(fallback)
            return fallback

        except LLMError as exc:
            logger.error("llm_error message=%s", exc)
            return str(exc)
        except Exception:
            logger.exception("unexpected_agent_error")
            return FALLBACK_RESPONSE


def create_agent(settings, include_knowledge: bool = True) -> SupportAgent:
    retriever: Retriever | None = None
    if include_knowledge:
        try:
            from ..rag.embeddings import Embedder
            from ..rag.vector_store import VectorStore

            store = VectorStore(settings.chroma_path)
            embedder = Embedder(settings.embedding_model)
            retriever = Retriever(
                store=store,
                embedder=embedder,
                top_k=settings.retrieval_top_k,
                min_score=settings.retrieval_min_score,
            )
        except Exception:
            logger.exception("knowledge_unavailable_continuing_without")

    timeout = 300.0 if settings.llm_provider == "ollama" else 60.0
    llm = LLMClient(
        api_key=settings.llm_api_key or "local",
        model=settings.llm_model,
        base_url=settings.base_url,
        timeout=timeout,
    )
    return SupportAgent(llm=llm, settings=settings, tools=build_tools(retriever))
