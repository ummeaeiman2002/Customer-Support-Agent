from __future__ import annotations

import logging

from .agent.agent import create_agent
from .agent.state import ConversationState
from .config.settings import ConfigError, load_settings
from .utils.logging import setup_logging

logger = logging.getLogger(__name__)

BANNER = """\
AI Customer Support Agent (v1)
Type your question, or 'exit' to quit.
"""

EMPTY_INPUT_MESSAGE = "I didn't catch that. Could you type your question again?"
UNEXPECTED_EXIT_MESSAGE = "\nGoodbye!"


def main() -> None:
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return

    setup_logging(settings.log_level)
    agent = create_agent(settings)
    state = ConversationState()

    print(BANNER)
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(UNEXPECTED_EXIT_MESSAGE)
            break

        if not user_text:
            print(f"Agent: {EMPTY_INPUT_MESSAGE}")
            continue
        if user_text.lower() in {"exit", "quit"}:
            print(UNEXPECTED_EXIT_MESSAGE)
            break

        logger.info("agent_request_received length=%d", len(user_text))
        reply = agent.run(user_text, state)
        print(f"Agent: {reply}")


if __name__ == "__main__":
    main()
