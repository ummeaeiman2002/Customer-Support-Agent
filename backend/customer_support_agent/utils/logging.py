from __future__ import annotations

import logging

_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format=_FORMAT)


def log_event(logger: logging.Logger, name: str, **fields: object) -> None:
    detail = " ".join(f"{key}={value}" for key, value in fields.items())
    logger.info("%s %s", name, detail)
