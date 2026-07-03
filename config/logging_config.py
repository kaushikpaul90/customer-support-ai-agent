"""
Logging configuration for the application.

Sets up structured JSON logging with OpenTelemetry instrumentation.

GitHub Copilot Prompt Used:
"Configure Python logging with JSON formatting, OpenTelemetry
instrumentation, and separate loggers for different modules"
"""

import logging
import logging.config
import json
import sys
from typing import Dict, Any
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format type ('json' or 'text')
    """
    
    if log_format == "json":
        _setup_json_logging(log_level)
    else:
        _setup_text_logging(log_level)


def _setup_json_logging(log_level: str) -> None:
    """Setup JSON structured logging."""
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # JSON formatter
    json_formatter = jsonlogger.JsonFormatter(
        fmt=(
            "%(timestamp)s %(level)s %(name)s %(message)s "
            "%(module)s %(funcName)s %(lineno)s"
        ),
        rename_fields={"timestamp": "time", "level": "severity"},
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    _configure_loggers(log_level)


def _setup_text_logging(log_level: str) -> None:
    """Setup text-based logging."""
    
    # Format string
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
    )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Configure specific loggers
    _configure_loggers(log_level)


def _configure_loggers(log_level: str) -> None:
    """Configure specific module loggers."""
    
    # Application loggers
    loggers = {
        "agents": log_level,
        "rag": log_level,
        "api": log_level,
        "evaluation": log_level,
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level))
    
    # Third-party loggers
    logging.getLogger("langchain").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.INFO)


class ContextualLogger:
    """
    Logger wrapper that adds context to log messages.
    
    Usage:
        logger = ContextualLogger("module_name")
        logger.info("Message", extra={"user_id": "123", "session_id": "abc"})
    """
    
    def __init__(self, name: str):
        """
        Initialize contextual logger.
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs) -> None:
        """Set context variables that will be included in all log messages."""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear all context variables."""
        self.context.clear()
    
    def _log(self, level: int, msg: str, *args, **kwargs) -> None:
        """Internal log method that adds context."""
        extra = kwargs.get("extra", {})
        extra.update(self.context)
        kwargs["extra"] = extra
        self.logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """Log info message."""
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, msg, *args, **kwargs)


__all__ = [
    "setup_logging",
    "ContextualLogger",
]
