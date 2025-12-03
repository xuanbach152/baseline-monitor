"""
Windows Agent Package
=====================
CIS Benchmark compliance agent for Windows 10/11.

This package contains:
- main.py: Main agent runner with auto-registration
- scanner.py: Windows CIS Benchmark scanner engine
- shell_executor.py: PowerShell command executor
- rule_loader.py: Rule loader từ JSON
- violation_reporter.py: Violation reporter tới backend

Usage:
    python agent/windows/main.py
"""

__version__ = "1.0.0"
__author__ = "Nguyen Xuan Bach"
