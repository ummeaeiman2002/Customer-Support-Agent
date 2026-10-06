from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from openai import (
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base error for LLM communication problems."""


class AuthError(LLMError):
    pass


class TimeoutLLMError(LLMError):
    pass


class RateLimitLLMError(LLMError):
    pass


class MalformedResponseError(LLMError):
    pass


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


def _parse_tool_calls(raw_calls: object) -> list[ToolCall]:
    parsed: list[ToolCall] = []
    for call in raw_calls or []:
        raw_arguments = call.function.arguments or "{}"
        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError:
            arguments = {"__invalid__": raw_arguments}
        if not isinstance(arguments, dict):
            arguments = {"__invalid__": arguments}
        parsed.append(
            ToolCall(id=call.id, name=call.function.name, arguments=arguments)
        )
    return parsed


class LLMClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        if base_url:
            self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        else:
            self._client = OpenAI(api_key=api_key, timeout=timeout)
        self._model = model

    def chat(
        self, messages: list[dict], tools: list[dict] | None = None
    ) -> LLMResponse:
        request: dict = {"model": self._model, "messages": messages}
        if tools:
            request["tools"] = tools

        logger.debug("llm_request model=%s messages=%d", self._model, len(messages))
        try:
            completion = self._client.chat.completions.create(**request)
        except AuthenticationError as exc:
            raise AuthError("Invalid API key. Check LLM_API_KEY in .env.") from exc
        except RateLimitError as exc:
            raise RateLimitLLMError(
                "Rate limit or quota exceeded. Try again shortly."
            ) from exc
        except APITimeoutError as exc:
            raise TimeoutLLMError("The AI service timed out. Try again.") from exc
        except APIStatusError as exc:
            raise LLMError(f"AI service error (status {exc.status_code}).") from exc

        try:
            choice = completion.choices[0]
            message = choice.message
        except (IndexError, AttributeError) as exc:
            raise MalformedResponseError(
                "The AI service returned an unexpected response."
            ) from exc

        return LLMResponse(
            text=message.content,
            tool_calls=_parse_tool_calls(message.tool_calls),
        )
