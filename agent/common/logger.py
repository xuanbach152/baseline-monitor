"""
Logging Module
==============
Setup logging với file rotation.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_file: str = "./logs/agent.log",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    console_output: bool = True,
    name: str = "agent"
) -> logging.Logger:
    """
    Setup logging với file rotation.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        max_bytes: Max file size trước khi rotate
        backup_count: Số file backup giữ lại
        console_output: In ra console không?
        name: Logger name
        
    Returns:
        Logger instance
    """
    # Tạo logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler với rotation
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (nếu cần)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "agent") -> logging.Logger:
    """
    Get logger đã setup.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


if __name__ == "__main__":
    """Test logger."""
    print("=" * 60)
    print("🧪 TESTING Logger")
    print("=" * 60)
    
    # Test với default config
    logger = setup_logger(
        log_level="DEBUG",
        log_file="./logs/test.log",
        console_output=True
    )
    
    print("\n📝 Testing log levels:\n")
    
    logger.debug("🐛 This is a DEBUG message")
    logger.info("ℹ️  This is an INFO message")
    logger.warning("⚠️  This is a WARNING message")
    logger.error("❌ This is an ERROR message")
    logger.critical("🔥 This is a CRITICAL message")
    
    print("\n" + "=" * 60)
    print("✅ Check ./logs/test.log for file output")
    print("=" * 60)
