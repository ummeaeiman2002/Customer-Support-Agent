from customer_support_agent.agent.agent import SupportAgent
from customer_support_agent.agent.state import ConversationState
from customer_support_agent.config.settings import load_settings
from customer_support_agent.llm.client import LLMResponse, ToolCall


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat(self, messages, tools=None):
        self.calls.append({"messages": messages, "tools": tools})
        return self.responses.pop(0)


def make_agent(fake_llm, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    settings = load_settings()
    return SupportAgent(llm=fake_llm, settings=settings)


def test_normal_question(monkeypatch):
    fake = FakeLLM([LLMResponse(text="Hello! How can I help you?")])
    agent = make_agent(fake, monkeypatch)

    reply = agent.run("Hi")

    assert reply == "Hello! How can I help you?"
    assert fake.calls[0]["messages"][0]["role"] == "system"


def test_tool_question_uses_calculator(monkeypatch):
    fake = FakeLLM(
        [
            LLMResponse(
                tool_calls=[
                    ToolCall(id="call_1", name="calculator", arguments={"expression": "49 * 3"})
                ]
            ),
            LLMResponse(text="The total is 147."),
        ]
    )
    agent = make_agent(fake, monkeypatch)
    state = ConversationState()

    reply = agent.run("What is 49 times 3?", state)

    assert reply == "The total is 147."
    assert len(fake.calls) == 2
    tool_message = fake.calls[1]["messages"][-1]
    assert tool_message["role"] == "tool"
    assert tool_message["content"] == "147"


def test_invalid_tool_arguments_return_error_result(monkeypatch):
    fake = FakeLLM(
        [
            LLMResponse(
                tool_calls=[
                    ToolCall(id="call_1", name="calculator", arguments={"expression": "1 / 0"})
                ]
            ),
            LLMResponse(text="That expression cannot be evaluated."),
        ]
    )
    agent = make_agent(fake, monkeypatch)

    reply = agent.run("compute 1/0", ConversationState())

    assert reply == "That expression cannot be evaluated."
    tool_message = fake.calls[1]["messages"][-1]
    assert tool_message["content"].startswith("Error:")


def test_unknown_tool_is_rejected(monkeypatch):
    fake = FakeLLM(
        [
            LLMResponse(
                tool_calls=[ToolCall(id="call_1", name="rm_rf", arguments={"path": "/"})]
            ),
            LLMResponse(text="I can't do that."),
        ]
    )
    agent = make_agent(fake, monkeypatch)

    agent.run("delete everything", ConversationState())

    tool_message = fake.calls[1]["messages"][-1]
    assert "unknown tool" in tool_message["content"]


def test_tool_loop_is_bounded(monkeypatch):
    calls = [
        LLMResponse(
            tool_calls=[
                ToolCall(id=f"call_{i}", name="calculator", arguments={"expression": "1 + 1"})
            ]
        )
        for i in range(10)
    ]
    fake = FakeLLM(calls)
    agent = make_agent(fake, monkeypatch)

    reply = agent.run("loop forever", ConversationState())

    assert len(fake.calls) <= 5
    assert "try again" in reply.lower()


def test_unknown_question_returns_fallback_without_tools(monkeypatch):
    fake = FakeLLM([LLMResponse(text="I'm not sure.")])
    agent = make_agent(fake, monkeypatch)

    agent.run("blah blah", ConversationState())

    assert fake.calls[0]["tools"]


def test_state_history_truncated(monkeypatch):
    fake = FakeLLM([LLMResponse(text=f"reply {i}") for i in range(30)])
    agent = make_agent(fake, monkeypatch)
    state = ConversationState()

    for i in range(30):
        agent.run(f"message {i}", state)

    assert len(state.messages) <= 20


def test_search_knowledge_tool_feeds_answer(monkeypatch):
    from customer_support_agent.agent.agent import build_tools

    class FakeRetriever:
        def search(self, query):
            return ["30 days refund window chunk"]

        def format_context(self, chunks):
            return " | ".join(chunks)

    fake = FakeLLM(
        [
            LLMResponse(
                tool_calls=[
                    ToolCall(
                        id="call_1",
                        name="search_knowledge",
                        arguments={"query": "refund window"},
                    )
                ]
            ),
            LLMResponse(text="Refunds are possible within 30 days."),
        ]
    )
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    settings = load_settings()
    agent = SupportAgent(llm=fake, settings=settings, tools=build_tools(FakeRetriever()))

    reply = agent.run("What is the refund window?", ConversationState())

    assert reply == "Refunds are possible within 30 days."
    tool_msg = fake.calls[1]["messages"][-1]
    assert tool_msg["role"] == "tool"
    assert "30 days" in tool_msg["content"]


def test_knowledge_not_advertised_without_retriever(monkeypatch):
    fake = FakeLLM([LLMResponse(text="ok")])
    agent = make_agent(fake, monkeypatch)

    agent.run("hi", ConversationState())

    tool_names = [t["function"]["name"] for t in fake.calls[0]["tools"]]
    assert tool_names == ["calculator"]
