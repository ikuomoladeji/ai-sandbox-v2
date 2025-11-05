"""
Production-grade logging module for TPRM system
Provides structured logging with rotation, multiple handlers, and security
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from config import Config

class TPRMLogger:
    """Centralized logging configuration for TPRM system"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger instance

        Args:
            name: Logger name (typically __name__)

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # Console handler with color coding
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)-8s | %(name)s | %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        # File handler with rotation
        Config.LOGS_DIR.mkdir(exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(Config.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def log_api_call(cls, logger: logging.Logger, endpoint: str, status: str, duration: float = None):
        """
        Log API call with structured information

        Args:
            logger: Logger instance
            endpoint: API endpoint called
            status: Call status (success/failure)
            duration: Optional duration in seconds
        """
        msg = f"API Call: {endpoint} | Status: {status}"
        if duration:
            msg += f" | Duration: {duration:.2f}s"

        if status == "success":
            logger.info(msg)
        else:
            logger.error(msg)

    @classmethod
    def log_user_action(cls, logger: logging.Logger, action: str, details: dict = None):
        """
        Log user action for audit trail

        Args:
            logger: Logger instance
            action: Action performed
            details: Optional additional details
        """
        msg = f"User Action: {action}"
        if details:
            msg += f" | Details: {details}"
        logger.info(msg)

    @classmethod
    def log_security_event(cls, logger: logging.Logger, event: str, severity: str = "warning"):
        """
        Log security-related event

        Args:
            logger: Logger instance
            event: Security event description
            severity: Event severity (info/warning/critical)
        """
        msg = f"SECURITY: {event}"

        if severity == "critical":
            logger.critical(msg)
        elif severity == "warning":
            logger.warning(msg)
        else:
            logger.info(msg)

# Convenience function for quick logger access
def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return TPRMLogger.get_logger(name)
