import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import dspy
import litellm
from rich.logging import RichHandler


# Custom file handler that auto-flushes after each log entry
class AutoFlushFileHandler(logging.FileHandler):
    """FileHandler that automatically flushes after each emit for real-time logging."""

    def emit(self, record):
        super().emit(record)
        self.flush()


# Logger configuration state
_LOGGER_NAME = "elysia"
_DEFAULT_CONSOLE_LEVEL = logging.WARNING
_DEFAULT_FILE_LEVEL = logging.DEBUG
_LOG_DIR = Path(__file__).resolve().parents[4] / "logs"
_logger = logging.getLogger(_LOGGER_NAME)
_logger.propagate = True
_configured = False
_managed_handlers: Dict[str, logging.Handler] = {}


def _coerce_level(level: int | str) -> int:
    """Translate string/int log levels into logging constants."""
    if isinstance(level, int):
        return level

    resolved = logging.getLevelName(level.upper())
    if isinstance(resolved, int):
        return resolved
    raise ValueError(f"Unsupported log level: {level}")


def configure_logging(
    *,
    console_level: int | str = _DEFAULT_CONSOLE_LEVEL,
    file_level: int | str = _DEFAULT_FILE_LEVEL,
    force: bool = False,
    log_dir: Optional[Path | str] = None,
) -> logging.Logger:
    """Configure root logging with rich console + auto-flush file handlers."""

    global _configured, _managed_handlers

    if _configured and not force:
        return _logger

    root_logger = logging.getLogger()

    # Remove previously managed handlers to avoid duplicates during reconfiguration
    for handler in list(root_logger.handlers):
        if getattr(handler, "_elysia_managed", False):
            root_logger.removeHandler(handler)

    resolved_console_level = _coerce_level(console_level)
    resolved_file_level = _coerce_level(file_level)

    # Console handler with rich formatting
    console_handler = RichHandler(rich_tracebacks=True, markup=False)
    console_handler.setLevel(resolved_console_level)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler._elysia_managed = True  # type: ignore[attr-defined]

    # File handler with detailed formatting and auto-flush
    destination_dir = Path(log_dir) if log_dir else _LOG_DIR
    destination_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = destination_dir / f"backend-{timestamp}.log"

    file_handler = AutoFlushFileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(resolved_file_level)
    file_formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    file_handler._elysia_managed = True  # type: ignore[attr-defined]

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(min(resolved_console_level, resolved_file_level))

    _managed_handlers = {"console": console_handler, "file": file_handler}

    # Ensure the named logger simply propagates to root handlers
    _logger.handlers = []
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = True

    # Set noise-prone third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("starlette").setLevel(logging.INFO)
    logging.getLogger("grpc").setLevel(logging.INFO)
    logging.getLogger("grpc._channel").setLevel(logging.WARNING)
    logging.getLogger("dspy").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM Router").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM Proxy").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("unstructured").setLevel(logging.WARNING)
    logging.getLogger("pdfminer").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    _configured = True
    return _logger


def get_logger(auto_configure: bool = True) -> logging.Logger:
    """Return the named logger, configuring the system on demand if requested."""

    if auto_configure and not _configured:
        configure_logging()
    return _logger


def set_log_level(level: int | str):
    """Set the level for the root logger and managed handlers."""

    numeric_level = _coerce_level(level)

    if not _configured:
        configure_logging()

    logger = get_logger(auto_configure=False)
    logger.setLevel(numeric_level)
    logging.getLogger().setLevel(numeric_level)

    for handler in _managed_handlers.values():
        handler.setLevel(numeric_level)


# Initialize the logger
logger = get_logger(auto_configure=False)

dspy.disable_litellm_logging()
dspy.disable_logging()
litellm.suppress_debug_info = True
