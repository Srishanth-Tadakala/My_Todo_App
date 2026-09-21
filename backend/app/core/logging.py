"""
Structured Logging Configuration
Provides consistent logging with secret sanitization.
"""

import logging
import re
import sys
from typing import Any, Dict

# Sensitive keys to sanitize in logs
SENSITIVE_PATTERNS = [
    re.compile(r"(password|token|secret|key|authorization|bearer)\s*[:=]\s*['\"]?([^'\"\s,]+)", re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """Filter that sanitizes credentials, tokens, and secrets from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.sanitize(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.sanitize(str(v)) if any(s in k.lower() for s in ["token", "key", "pass", "secret"]) else v for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.sanitize(str(arg)) if isinstance(arg, str) else arg for arg in record.args)
        return True

    @staticmethod
    def sanitize(text: str) -> str:
        for pattern in SENSITIVE_PATTERNS:
            text = pattern.sub(r"\1=***REDACTED***", text)
        return text


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configures structured root logging for the application."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if already setup
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(handler)

    logger = logging.getLogger("todo_app")
    logger.setLevel(level)
    return logger


logger = setup_logging()
