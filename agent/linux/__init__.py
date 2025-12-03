"""
Linux Agent Package
===================
CIS Benchmark compliance agent for Ubuntu/Linux.

This package contains:
- main.py: Main agent runner with auto-registration
- scanner.py: Ubuntu CIS Benchmark scanner engine
- shell_executor.py: Bash command executor
- rule_loader.py: Rule loader từ JSON
- violation_reporter.py: Violation reporter tới backend

Usage:
    python agent/linux/main.py
"""

__version__ = "1.0.0"
__author__ = "Nguyen Xuan Bach"
