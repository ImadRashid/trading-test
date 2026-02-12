import json
import logging


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def structured_log(message: str, **fields: object) -> str:
    if not fields:
        return message
    return f"{message} | {json.dumps(fields, sort_keys=True, separators=(',', ':'))}"
