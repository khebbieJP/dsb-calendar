"""
Structured logging configuration with JSON format
"""

import logging
import sys
from typing import Optional, Dict, Any
from pythonjsonlogger import jsonlogger


class StructuredLogger:
    """
    Wrapper for structured logging with consistent context
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def _add_context(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Add context fields to log entry"""
        context = {}

        # Extract context fields from kwargs
        if 'request_id' in kwargs:
            context['requestId'] = kwargs.pop('request_id')
        if 'user_id' in kwargs:
            context['userId'] = kwargs.pop('user_id')
        if 'operation' in kwargs:
            context['operation'] = kwargs.pop('operation')

        # Merge with extra context if provided
        if extra:
            context.update(extra)

        # Add remaining kwargs as additional fields
        context.update(kwargs)

        return {'extra': {'context': context}} if context else {}

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message with context"""
        self.logger.info(message, **self._add_context(extra, **kwargs))

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message with context"""
        self.logger.warning(message, **self._add_context(extra, **kwargs))

    def error(self, message: str, exc_info: bool = False,
              extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message with context"""
        self.logger.error(message, exc_info=exc_info, **self._add_context(extra, **kwargs))

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message with context"""
        self.logger.debug(message, **self._add_context(extra, **kwargs))


def setup_structured_logging(app_name: str = 'dsb_converter',
                             level: int = logging.INFO) -> StructuredLogger:
    """
    Configure structured logging with JSON format

    Args:
        app_name: Name of the application/logger
        level: Logging level (default: INFO)

    Returns:
        StructuredLogger instance
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt='%(levelname)s %(message)s',
        rename_fields={'levelname': 'level'},
        timestamp=True
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return StructuredLogger(logger)
