"""
Centralized logging configuration for MCP Client.
All application logs go to /var/log/mcp-client/app.log
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory
LOG_DIR = Path("/var/log/mcp-client")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

# Custom formatter with timestamp, level, module, and message
class CustomFormatter(logging.Formatter):
    """Custom formatter with color support for console and detailed format"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, use_color=False):
        super().__init__()
        self.use_color = use_color
        
    def format(self, record):
        # Format: 2026-02-11 15:30:45 | INFO | module:line | message
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname
        module = f"{record.name}:{record.lineno}"
        message = record.getMessage()
        
        # Include exception info if present
        if record.exc_info:
            message += '\n' + self.formatException(record.exc_info)
        
        if self.use_color and level in self.COLORS:
            color = self.COLORS[level]
            reset = self.COLORS['RESET']
            return f"{timestamp} | {color}{level:8s}{reset} | {module:30s} | {message}"
        else:
            return f"{timestamp} | {level:8s} | {module:30s} | {message}"


def setup_logging(log_level=logging.INFO):
    """
    Setup centralized logging for the entire application.
    
    Logs go to:
    1. /var/log/mcp-client/app.log (file, with rotation)
    2. stdout (console, with colors)
    
    All loggers in the application will use this configuration.
    """
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # 1. FILE HANDLER with rotation (50MB per file, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(CustomFormatter(use_color=False))
    root_logger.addHandler(file_handler)
    
    # 2. CONSOLE HANDLER with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomFormatter(use_color=True))
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info("=" * 80)
    root_logger.info(f"MCP Client Application Starting - {datetime.now()}")
    root_logger.info(f"Log file: {LOG_FILE}")
    root_logger.info(f"Log level: {logging.getLevelName(log_level)}")
    root_logger.info("=" * 80)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)


# Module-level logger for this file
logger = get_logger(__name__)
