import logging
import json
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Minimal JSON logs that Render can index without leaking exception data."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "elevra-backend",
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
