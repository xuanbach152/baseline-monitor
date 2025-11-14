"""
Agent Common Module
===================
Module chứa các thành phần dùng chung cho cả Linux và Windows agent.

Các module:
- config: Đọc và validate cấu hình từ YAML
- logger: Logging system thống nhất
- http_client: HTTP client để giao tiếp với backend API
- models: Pydantic models cho data validation
- system_info: Thu thập thông tin hệ thống
"""

__version__ = "1.0.0"

# Import all modules
from .config import AgentConfig, get_config
from .logger import setup_logger, get_logger
from .http_client import BackendAPIClient
from .models import (
    ViolationReport,
    ViolationStatus,
    ScanResult,
    Rule,
    RuleSeverity,
    AgentStatus
)
from . import system_info

__all__ = [
    "AgentConfig",
    "get_config",
    "setup_logger",
    "get_logger",
    "BackendAPIClient",
    "ViolationReport",
    "ViolationStatus",
    "ScanResult",
    "Rule",
    "RuleSeverity",
    "AgentStatus",
    "system_info",
]
