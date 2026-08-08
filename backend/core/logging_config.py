"""
Centralized Logging Configuration
Replaces scattered print() and logging.basicConfig() calls
"""
import logging
import sys
from typing import Optional
from datetime import datetime

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Levels
    DEBUG = "\033[36m"     # Cyan
    INFO = "\033[32m"      # Green
    WARNING = "\033[33m"   # Yellow
    ERROR = "\033[31m"     # Red
    CRITICAL = "\033[35m"  # Magenta

    # Components
    AGENT = "\033[94m"     # Blue
    EMAIL = "\033[95m"     # Pink
    API = "\033[96m"       # Light Cyan

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis"""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.DEBUG,
        logging.INFO: Colors.INFO,
        logging.WARNING: Colors.WARNING,
        logging.ERROR: Colors.ERROR,
        logging.CRITICAL: Colors.CRITICAL,
    }

    LEVEL_EMOJIS = {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Add color and emoji
        level_color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        emoji = self.LEVEL_EMOJIS.get(record.levelno, "")

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Format message
        formatted = (
            f"{Colors.BOLD}{timestamp}{Colors.RESET} "
            f"{level_color}{emoji} {record.levelname:8s}{Colors.RESET} "
            f"{Colors.BOLD}[{record.name}]{Colors.RESET} "
            f"{record.getMessage()}"
        )

        # Add exception info if present
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted

class PlainFormatter(logging.Formatter):
    """Plain formatter for file output (no colors)"""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        formatted = (
            f"{timestamp} {record.levelname:8s} [{record.name}] {record.getMessage()}"
        )

        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """
    Configure application logging

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
    """
    # Remove existing handlers
    root = logging.getLogger()
    root.handlers.clear()

    # Set root level
    root.setLevel(getattr(logging, level.upper()))

    # Ensure UTF-8 output on Windows streams
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter())
    root.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(PlainFormatter())
        root.addHandler(file_handler)

    # Silence noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

# Default setup on import
setup_logging()
