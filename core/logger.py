"""
core/logger.py — XDG-compliant logging system for envkit
"""

import os
import re
import sys
import logging
from datetime import datetime
from pathlib import Path

# Sensitive patterns to redact
REDACT_PATTERNS = [
    re.compile(r'(password[:=]\s*)\S+', re.IGNORECASE),
    re.compile(r'(token[:=]\s*)\S+', re.IGNORECASE),
    re.compile(r'(secret[:=]\s*)\S+', re.IGNORECASE),
    re.compile(r'(PRIVATE KEY-----[\s\S]*?-----END)', re.IGNORECASE),
]

def sanitize(text: str) -> str:
    """Sanitize sensitive info from log strings."""
    result = text
    for pattern in REDACT_PATTERNS:
        result = pattern.sub(r'\1[REDACTED]', result)
    return result


class RedactingFormatter(logging.Formatter):
    def format(self, record):
        orig = super().format(record)
        return sanitize(orig)


def get_log_dir() -> Path:
    """Return XDG-compliant log directory: ~/.local/state/envkit/logs"""
    state_home = os.environ.get("XDG_STATE_HOME")
    if state_home:
        base = Path(state_home) / "envkit" / "logs"
    else:
        base = Path.home() / ".local" / "state" / "envkit" / "logs"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        base = Path("/tmp/envkit/logs")
        try:
            base.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
    return base


_GLOBAL_LOGGER = None


def setup_logger(session_name: str = "envkit") -> logging.Logger:
    """Configure file and console logging."""
    global _GLOBAL_LOGGER
    if _GLOBAL_LOGGER is not None:
        return _GLOBAL_LOGGER

    logger = logging.getLogger("envkit")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Avoid duplicate handlers
    if not logger.handlers:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = get_log_dir() / f"{session_name}_{timestamp}.log"

        formatter = RedactingFormatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File Handler
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except OSError:
            pass

        # Console Handler (INFO by default)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        console_fmt = RedactingFormatter("%(message)s")
        ch.setFormatter(console_fmt)
        logger.addHandler(ch)

    _GLOBAL_LOGGER = logger
    return logger


def get_logger() -> logging.Logger:
    global _GLOBAL_LOGGER
    if _GLOBAL_LOGGER is None:
        return setup_logger()
    return _GLOBAL_LOGGER
