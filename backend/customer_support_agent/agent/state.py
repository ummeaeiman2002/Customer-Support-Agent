from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConversationState:
    messages: list[dict] = field(default_factory=list)
    retrieved_context: str = ""
    turn_count: int = 0
    metadata: dict = field(default_factory=dict)

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})
        self.turn_count += 1

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})

    def add_assistant_tool_calls(self, raw_calls: list[dict]) -> None:
        self.messages.append({"role": "assistant", "content": None, "tool_calls": raw_calls})

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self.messages.append(
            {"role": "tool", "tool_call_id": tool_call_id, "content": content}
        )

    def clear_turn_context(self) -> None:
        self.retrieved_context = ""

    def truncate_history(self, keep_last: int = 20) -> None:
        if len(self.messages) > keep_last:
            self.messages = self.messages[-keep_last:]
