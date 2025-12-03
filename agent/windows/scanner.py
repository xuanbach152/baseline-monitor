#!/usr/bin/env python3
"""
Windows Scanner Engine Module
==============================
Core scanning logic để scan Windows CIS Benchmark rules và detect violations.

Usage:
    from agent.windows.scanner import run_scan
    
    scan_result = run_scan(
        agent_id=7,
        rules_path="agent/rules/windows_rules.json"
    )
    print(scan_result.summary())
"""

import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.common.models import ScanResult, ViolationReport, ViolationStatus, Rule
from agent.common import get_logger
from agent.windows.rule_loader import load_rules
from agent.windows.shell_executor import execute_command

logger = get_logger(__name__)


def run_scan(
    agent_id: int,
    rules_path: str,
    timeout_per_rule: int = 30
) -> ScanResult:
    """
    Run full scan của tất cả Windows rules.
    
    Luồng hoạt động:
    1. Load rules từ JSON file
    2. Loop qua từng rule:
       - Execute PowerShell audit command
       - Compare output với expected_output
       - Detect violation (PASS/FAIL/ERROR)
    3. Return ScanResult với list violations
    
    Args:
        agent_id: ID của agent đang scan
        rules_path: Path tới windows_rules.json
        timeout_per_rule: Timeout cho mỗi rule (default: 30s)
    
    Returns:
        ScanResult: Object chứa violations, metrics, summary
    
    Example:
        >>> result = run_scan(agent_id=7, rules_path="agent/rules/windows_rules.json")
        >>> print(f"Compliance: {result.compliance_rate:.1f}%")
        >>> print(f"Pass: {result.pass_count}, Fail: {result.fail_count}")
    """
    scan_started_at = datetime.now(UTC)
    
    logger.info("=" * 60)
    logger.info(" STARTING WINDOWS COMPLIANCE SCAN")
    logger.info("=" * 60)
    logger.info(f"Agent ID: {agent_id}")
    logger.info(f"Rules file: {rules_path}")
    logger.info(f"Started at: {scan_started_at.isoformat()}")
    
    # Initialize scan result
    scan_result = ScanResult(
        agent_id=agent_id,
        scan_started_at=scan_started_at
    )
    
    try:
        # 1. Load rules
        logger.info("\n📋 Loading rules...")
        rules = load_rules(rules_path)
        logger.info(f"✅ Loaded {len(rules)} rules")
        
        # Load expected outputs từ JSON
        expected_outputs = _load_expected_outputs(rules_path)
        
        scan_result.total_rules_checked = len(rules)
        
        # 2. Scan từng rule
        logger.info("\n🔍 Scanning rules...")
        logger.info("-" * 60)
        
        for idx, rule in enumerate(rules, 1):
            logger.info(f"\n[{idx}/{len(rules)}] Checking {rule.rule_id}: {rule.title}")
            logger.info(f"  Category: {rule.category} | Severity: {rule.severity}")
            
            # Get expected output cho rule này
            expected_output = expected_outputs.get(rule.rule_id)
            
            # Check rule
            violation = check_rule(
                agent_id=agent_id,
                rule=rule,
                expected_output=expected_output,
                timeout=timeout_per_rule
            )
            
            # Add violation to result
            scan_result.violations.append(violation)
            
            # Log status
            if violation.status == ViolationStatus.PASS:
                logger.info(f"  ✅ PASS")
            elif violation.status == ViolationStatus.FAIL:
                logger.warning(f"  ❌ FAIL - {violation.details}")
            else:
                logger.error(f"  ⚠️  ERROR - {violation.details}")
        
        # 3. Finalize scan
        scan_result.scan_completed_at = datetime.now(UTC)
        
        # Log summary
        logger.info("\n" + "=" * 60)
        logger.info(" SCAN COMPLETED")
        logger.info("=" * 60)
        logger.info(scan_result.summary())
        logger.info("=" * 60)
        
        return scan_result
        
    except Exception as e:
        logger.error(f"❌ Scan failed with error: {e}", exc_info=True)
        scan_result.errors.append(f"Scan failed: {str(e)}")
        scan_result.scan_completed_at = datetime.now(UTC)
        return scan_result


def check_rule(
    agent_id: int,
    rule: Rule,
    expected_output: Optional[str],
    timeout: int = 30
) -> ViolationReport:
    """
    Check một Windows rule và return ViolationReport.
    
    Logic:
    1. Execute PowerShell audit command (check_expression)
    2. Compare output với expected_output
    3. Determine status: PASS/FAIL/ERROR
    
    Args:
        agent_id: ID của agent
        rule: Rule object cần check
        expected_output: Output mong đợi (từ JSON)
        timeout: Timeout cho command
    
    Returns:
        ViolationReport: Report với status PASS/FAIL/ERROR
    """
    logger.debug(f"  Executing: {rule.check_expression}")
    
    # Execute PowerShell command
    exit_code, stdout, stderr = execute_command(
        cmd=rule.check_expression,
        timeout=timeout,
        use_powershell=True
    )
    
    # Determine status
    if exit_code == -1:
        # Timeout hoặc exception
        status = ViolationStatus.ERROR
        details = f"Command execution failed: {stderr}"
        
    elif exit_code != 0:
        # Command failed
        if expected_output and stdout:
            # Nếu có output, compare với expected
            status, details = _compare_output(stdout, expected_output)
        else:
            # Không có output → ERROR
            status = ViolationStatus.ERROR
            details = f"Command failed with exit code {exit_code}: {stderr}"
    
    else:
        # Command success (exit_code == 0)
        if expected_output:
            status, details = _compare_output(stdout, expected_output)
        else:
            # Không có expected_output → assume PASS
            status = ViolationStatus.PASS
            details = "Command executed successfully"
    
    # Create violation report
    violation = ViolationReport(
        agent_id=agent_id,
        rule_id=rule.rule_id,
        status=status,
        details=details,
        raw_output=stdout if stdout else stderr
    )
    
    return violation


def _compare_output(actual: str, expected: str) -> tuple[ViolationStatus, str]:
    """
    Compare actual output với expected output.
    
    Logic:
    - Exact match → PASS
    - Substring match → PASS (flexible)
    - No match → FAIL
    
    Args:
        actual: Output thực tế từ command
        expected: Output mong đợi
    
    Returns:
        tuple[ViolationStatus, str]: (status, details_message)
    """
    actual = actual.strip()
    expected = expected.strip()
    
    # Exact match
    if actual == expected:
        return ViolationStatus.PASS, "Output matches expected value"
    
    # Substring match (flexible)
    if expected in actual:
        return ViolationStatus.PASS, f"Output contains expected value: '{expected}'"
    
    # Case-insensitive match (for True/False, Enabled/Disabled)
    if actual.lower() == expected.lower():
        return ViolationStatus.PASS, "Output matches expected value (case-insensitive)"
    
    # No match → FAIL
    return (
        ViolationStatus.FAIL,
        f"Expected: '{expected}', Got: '{actual}'"
    )


def _load_expected_outputs(rules_path: str) -> dict:
    """
    Load expected_output từ windows_rules.json.
    
    Rule model không có field expected_output, nhưng cần nó để compare.
    
    Args:
        rules_path: Path tới JSON file
    
    Returns:
        dict: Mapping từ rule_id → expected_output
    
    Example:
        {"WIN-01": "Disabled", "WIN-02": "True"}
    """
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
        
        expected_outputs = {}
        for rule_dict in rules_data:
            rule_id = rule_dict.get('id')
            expected_output = rule_dict.get('expected_output')
            if rule_id and expected_output:
                expected_outputs[rule_id] = expected_output
        
        logger.debug(f"Loaded expected outputs for {len(expected_outputs)} rules")
        return expected_outputs
        
    except Exception as e:
        logger.error(f"Failed to load expected outputs: {e}")
        return {}


def test_scanner():
    """Test scanner với windows_rules.json."""
    print("=" * 70)
    print(" TESTING Windows Scanner Engine")
    print("=" * 70)
    
    # Check if running on Windows
    import platform
    if platform.system() != "Windows":
        print(f"\n⚠️  This scanner is designed for Windows only.")
        print(f"   Current OS: {platform.system()}")
        print("\n   To test, run this on a Windows machine.")
        return
    
    # Test với agent_id giả
    agent_id = 999
    rules_path = "agent/rules/windows_rules.json"
    
    print(f"\nAgent ID: {agent_id}")
    print(f"Rules file: {rules_path}")
    print("\n" + "=" * 70)
    print("Starting scan...")
    print("=" * 70)
    
    # Run scan
    scan_result = run_scan(
        agent_id=agent_id,
        rules_path=rules_path,
        timeout_per_rule=30
    )
    
    # Print detailed results
    print("\n" + "=" * 70)
    print(" DETAILED RESULTS")
    print("=" * 70)
    
    # Group by status
    pass_violations = [v for v in scan_result.violations if v.status == ViolationStatus.PASS]
    fail_violations = [v for v in scan_result.violations if v.status == ViolationStatus.FAIL]
    error_violations = [v for v in scan_result.violations if v.status == ViolationStatus.ERROR]
    
    # Show passes
    if pass_violations:
        print(f"\n✅ PASSED ({len(pass_violations)} rules):")
        print("-" * 70)
        for v in pass_violations:
            print(f"  • {v.rule_id}: {v.details}")
    
    # Show failures
    if fail_violations:
        print(f"\n❌ FAILED ({len(fail_violations)} rules):")
        print("-" * 70)
        for v in fail_violations:
            print(f"  • {v.rule_id}: {v.details}")
            if v.raw_output:
                print(f"    Raw output: {v.raw_output[:100]}")
    
    # Show errors
    if error_violations:
        print(f"\n⚠️  ERRORS ({len(error_violations)} rules):")
        print("-" * 70)
        for v in error_violations:
            print(f"  • {v.rule_id}: {v.details}")
    
    # Summary
    print("\n" + "=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print(scan_result.summary())
    
    # Duration
    if scan_result.scan_completed_at:
        duration = (scan_result.scan_completed_at - scan_result.scan_started_at).total_seconds()
        print(f"  ⏱️  Duration: {duration:.2f}s")
    
    print("=" * 70)
    
    return scan_result


if __name__ == "__main__":
    """Test scanner."""
    import sys
    
    try:
        scan_result = test_scanner()
        
        if scan_result is None:
            print("\n⚠️  Scanner test skipped (not on Windows)")
            sys.exit(0)
        
        # Exit with code based on compliance
        if scan_result.fail_count > 0:
            print(f"\n⚠️  {scan_result.fail_count} rule(s) failed - system is NOT compliant")
            sys.exit(1)
        elif scan_result.error_count > 0:
            print(f"\n⚠️  {scan_result.error_count} rule(s) had errors - scan incomplete")
            sys.exit(2)
        else:
            print(f"\n✅ All rules passed - system is COMPLIANT!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Scanner test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
