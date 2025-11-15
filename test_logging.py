"""
Tests for structured logging functionality
"""

import json
import logging
from io import StringIO
from dsb_converter.logging_config import setup_structured_logging, StructuredLogger


class TestStructuredLogging:
    """Test suite for structured logging"""

    def test_logger_setup(self):
        """Test that logger is properly configured"""
        logger = setup_structured_logging('test_logger')
        assert isinstance(logger, StructuredLogger)
        assert logger.logger.name == 'test_logger'

    def test_json_output_format(self):
        """Test that logs are output in JSON format with required fields"""
        # Capture log output
        log_output = StringIO()
        handler = logging.StreamHandler(log_output)

        logger = setup_structured_logging('test_json_logger')
        # Replace the handler to capture output
        logger.logger.handlers.clear()
        logger.logger.addHandler(handler)

        # Need to also add the formatter
        from pythonjsonlogger import jsonlogger
        formatter = jsonlogger.JsonFormatter(
            fmt='%(levelname)s %(message)s',
            rename_fields={'levelname': 'level'},
            timestamp=True
        )
        handler.setFormatter(formatter)

        # Log a message
        logger.info(
            "Test message",
            request_id="req-123",
            operation="test_operation"
        )

        # Get the output and parse as JSON
        output = log_output.getvalue().strip()
        log_entry = json.loads(output)

        # Verify required fields are present
        assert 'timestamp' in log_entry
        assert 'level' in log_entry
        assert 'message' in log_entry
        assert 'context' in log_entry

        # Verify field values
        assert log_entry['level'] == 'INFO'
        assert log_entry['message'] == 'Test message'
        assert log_entry['context']['requestId'] == 'req-123'
        assert log_entry['context']['operation'] == 'test_operation'

    def test_different_log_levels(self):
        """Test that different log levels are correctly recorded"""
        log_output = StringIO()
        handler = logging.StreamHandler(log_output)

        logger = setup_structured_logging('test_levels_logger')
        logger.logger.handlers.clear()
        logger.logger.addHandler(handler)

        from pythonjsonlogger import jsonlogger
        formatter = jsonlogger.JsonFormatter(
            fmt='%(levelname)s %(message)s',
            rename_fields={'levelname': 'level'},
            timestamp=True
        )
        handler.setFormatter(formatter)

        # Test different levels
        logger.info("Info message", operation="info_op")
        logger.warning("Warning message", operation="warning_op")
        logger.error("Error message", operation="error_op")

        # Parse all log entries
        lines = log_output.getvalue().strip().split('\n')
        assert len(lines) == 3

        info_log = json.loads(lines[0])
        warning_log = json.loads(lines[1])
        error_log = json.loads(lines[2])

        assert info_log['level'] == 'INFO'
        assert warning_log['level'] == 'WARNING'
        assert error_log['level'] == 'ERROR'

    def test_context_fields(self):
        """Test that context fields are properly included"""
        log_output = StringIO()
        handler = logging.StreamHandler(log_output)

        logger = setup_structured_logging('test_context_logger')
        logger.logger.handlers.clear()
        logger.logger.addHandler(handler)

        from pythonjsonlogger import jsonlogger
        formatter = jsonlogger.JsonFormatter(
            fmt='%(levelname)s %(message)s',
            rename_fields={'levelname': 'level'},
            timestamp=True
        )
        handler.setFormatter(formatter)

        # Log with multiple context fields
        logger.info(
            "Context test",
            request_id="req-456",
            user_id="user-789",
            operation="test_context",
            custom_field="custom_value"
        )

        output = log_output.getvalue().strip()
        log_entry = json.loads(output)

        context = log_entry['context']
        assert context['requestId'] == 'req-456'
        assert context['userId'] == 'user-789'
        assert context['operation'] == 'test_context'
        assert context['custom_field'] == 'custom_value'
