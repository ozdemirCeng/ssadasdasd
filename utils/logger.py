"""
Logger Configuration
"""

from loguru import logger
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import LogConfig, LOGS_DIR

# Log yapılandırması
logger.remove()

# Console output
logger.add(
    sys.stdout,
    format=LogConfig.FORMAT,
    level=LogConfig.LEVEL,
    colorize=True
)

# File output
logger.add(
    LogConfig.LOG_FILE,
    format=LogConfig.FORMAT,
    level="DEBUG",
    rotation=LogConfig.ROTATION,
    retention=LogConfig.RETENTION,
    compression=LogConfig.COMPRESSION
)

# Error log
logger.add(
    LogConfig.ERROR_LOG_FILE,
    format=LogConfig.FORMAT,
    level="ERROR",
    rotation=LogConfig.ROTATION,
    retention=LogConfig.RETENTION,
    compression=LogConfig.COMPRESSION
)

__all__ = ['logger']