#!/usr/bin/env python3
"""
Violation Reporter Module
==========================
Module để report violations tới backend API.

Usage:
    from agent.linux.violation_reporter import report_violations
    from agent.common import BackendAPIClient
    
    client = BackendAPIClient(api_url="http://localhost:8000", api_token="...")
    success = report_violations(client, scan_result)
"""

import sys
from pathlib import Path
from typing import List


sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.common.models import ScanResult, ViolationReport, ViolationStatus
from agent.common.http_client import BackendAPIClient
from agent.common import get_logger


logger = get_logger(__name__)


def report_violations(
    client: BackendAPIClient,
    scan_result: ScanResult,
    report_pass: bool = False
) -> bool:
    """
    Report violations tới backend API.
    
    Chỉ report FAIL violations (mặc định), không report PASS để tiết kiệm bandwidth.
    ERROR violations cũng được report để backend biết có vấn đề.
    
    Args:
        client: BackendAPIClient instance
        scan_result: ScanResult từ scanner
        report_pass: Có report PASS violations không (default: False)
    
    Returns:
        bool: True nếu report thành công, False nếu có lỗi
    
    Example:
        >>> client = BackendAPIClient("http://backend:8000", "token123")
        >>> success = report_violations(client, scan_result)
        >>> if success:
        ...     print("Violations reported successfully")
    """
    logger.info("=" * 60)
    logger.info("REPORTING VIOLATIONS TO BACKEND")
    logger.info("=" * 60)
    logger.info(f"Total violations: {len(scan_result.violations)}")
    
    # Filter violations to report
    violations_to_report = []
    for violation in scan_result.violations:
        if violation.status == ViolationStatus.FAIL:
            violations_to_report.append(violation)
        elif violation.status == ViolationStatus.ERROR:
            violations_to_report.append(violation)
        elif violation.status == ViolationStatus.PASS and report_pass:
            violations_to_report.append(violation)
    
    logger.info(f"Violations to report: {len(violations_to_report)}")
    logger.info(f"  FAIL: {sum(1 for v in violations_to_report if v.status == ViolationStatus.FAIL)}")
    logger.info(f"  ERROR: {sum(1 for v in violations_to_report if v.status == ViolationStatus.ERROR)}")
    if report_pass:
        logger.info(f"  PASS: {sum(1 for v in violations_to_report if v.status == ViolationStatus.PASS)}")
    
    if not violations_to_report:
        logger.info(" No violations to report - system is compliant!")
        return True
    
    # Report violations
    success_count = 0
    failed_count = 0
    
    logger.info("\n" + "-" * 60)
    logger.info("Reporting violations...")
    logger.info("-" * 60)
    
    for idx, violation in enumerate(violations_to_report, 1):
        logger.info(f"\n[{idx}/{len(violations_to_report)}] Reporting {violation.rule_id}...")
        
        success = _report_single_violation(client, violation)
        
        if success:
            logger.info(f"  Reported successfully")
            success_count += 1
        else:
            logger.error(f"  Failed to report")
            failed_count += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("REPORTING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total violations: {len(violations_to_report)}")
    logger.info(f" Reported successfully: {success_count}")
    logger.info(f" Failed to report: {failed_count}")
    
    if failed_count > 0:
        logger.warning(f" {failed_count} violation(s) failed to report")
        return False
    else:
        logger.info(" All violations reported successfully!")
        return True


def _report_single_violation(
    client: BackendAPIClient,
    violation: ViolationReport
) -> bool:
    """
    Report một violation tới backend.
    
    POST tới /api/v1/violations/from-agent với format:
    {
        "agent_id": 7,
        "agent_rule_id": "UBU-01",  # Backend sẽ convert sang rule_id
        "message": "Expected 'no', got 'yes'",
        "status": "FAIL"
    }
    
    Args:
        client: BackendAPIClient instance
        violation: ViolationReport object
    
    Returns:
        bool: True nếu thành công, False nếu lỗi
    """
    # Prepare payload
    payload = {
        "agent_id": violation.agent_id,
        "agent_rule_id": violation.rule_id,  # "UBU-01", "UBU-02", etc.
        "message": violation.details or "Rule violation detected",
        "confidence_score": 1.0  # Default confidence
        # Note: Backend schema không chấp nhận 'status' và 'raw_output'
        # Có thể thêm vào message nếu cần
    }
    
    # Add raw_output to message if exists
    if violation.raw_output:
        payload["message"] += f"\nRaw output: {violation.raw_output[:200]}"
    
    logger.debug(f"  Payload: {payload}")
    
    try:
        # POST tới /api/v1/violations/from-agent
        response = client.post(
            endpoint="/api/v1/violations/from-agent",
            data=payload
        )
        
        if response and response.get("id"):
            logger.debug(f"  Backend violation ID: {response.get('id')}")
            return True
        else:
            logger.error(f"  Invalid response from backend: {response}")
            return False
            
    except Exception as e:
        logger.error(f"  Failed to report violation: {e}")
        return False


def report_violations_batch(
    client: BackendAPIClient,
    scan_result: ScanResult,
    report_pass: bool = False
) -> bool:
    """
    Report violations theo batch (tất cả cùng lúc) thay vì từng cái.
    
    TODO: Implement batch endpoint ở backend (/api/v1/violations/batch)
    để giảm số HTTP requests.
    
    Args:
        client: BackendAPIClient instance
        scan_result: ScanResult từ scanner
        report_pass: Có report PASS violations không
    
    Returns:
        bool: True nếu thành công, False nếu lỗi
    """
    # TODO: Implement khi backend có batch endpoint
    logger.warning("Batch reporting not implemented yet - falling back to individual reporting")
    return report_violations(client, scan_result, report_pass=report_pass)


def test_violation_reporter():
    """Test violation reporter với mock data."""
    print("=" * 70)
    print("🧪 TESTING Violation Reporter")
    print("=" * 70)
    
    # NOTE: Test này cần backend đang chạy!
    print("\n⚠️  This test requires backend to be running!")
    print("   Backend URL: http://localhost:8000")
    print("   Make sure backend is up before running this test.")
    
    # Import dependencies
    from datetime import datetime, UTC
    from agent.common import get_config
    
    # Load config
    try:
        config = get_config("config.yaml")
    except FileNotFoundError:
        print("\n❌ config.yaml not found!")
        print("   Run setup.py first to generate config")
        return False
    
    # Create client
    client = BackendAPIClient(
        api_url=config.api_url,
        api_token=config.api_token,
        timeout=config.api_timeout,
        retry_attempts=config.api_retry_attempts
    )
    
    # Check backend health
    print("\n" + "-" * 70)
    print("Checking backend health...")
    if not client.health_check():
        print("❌ Backend is not reachable!")
        print(f"   URL: {config.api_url}")
        print("   Please start backend first")
        return False
    
    print("✅ Backend is healthy")
    
    # Get agent_id from cache
    agent_id = config.agent_id
    if not agent_id:
        print("\n❌ No agent_id found in cache!")
        print("   Run agent/linux/main.py first to register")
        return False
    
    print(f"✅ Agent ID: {agent_id}")
    
    # Create mock scan result
    print("\n" + "-" * 70)
    print("Creating mock scan result...")
    
    scan_result = ScanResult(
        agent_id=agent_id,
        scan_started_at=datetime.now(UTC),
        total_rules_checked=5
    )
    
    # Add mock violations
    scan_result.violations.extend([
        ViolationReport(
            agent_id=agent_id,
            rule_id="UBU-01",
            status=ViolationStatus.FAIL,
            details="Root SSH login is enabled (expected: disabled)",
            raw_output="PermitRootLogin yes"
        ),
        ViolationReport(
            agent_id=agent_id,
            rule_id="UBU-02",
            status=ViolationStatus.FAIL,
            details="UFW firewall is not active",
            raw_output="Status: inactive"
        ),
        ViolationReport(
            agent_id=agent_id,
            rule_id="UBU-03",
            status=ViolationStatus.PASS,
            details="Auditd service is enabled",
            raw_output="enabled"
        ),
        ViolationReport(
            agent_id=agent_id,
            rule_id="UBU-04",
            status=ViolationStatus.ERROR,
            details="Failed to check automatic updates",
            raw_output=""
        ),
    ])
    
    scan_result.scan_completed_at = datetime.now(UTC)
    
    print(f"✅ Mock scan result created:")
    print(scan_result.summary())
    
    # Report violations
    print("\n" + "=" * 70)
    print("Testing violation reporting...")
    print("=" * 70)
    
    success = report_violations(
        client=client,
        scan_result=scan_result,
        report_pass=False  # Don't report PASS violations
    )
    
    if success:
        print("\n" + "=" * 70)
        print("✅ VIOLATION REPORTER TEST PASSED!")
        print("=" * 70)
        print("\n💡 Check backend to verify violations:")
        print(f"   GET {config.api_url}/api/v1/violations")
        print(f"   GET {config.api_url}/api/v1/agents/{agent_id}/violations")
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ VIOLATION REPORTER TEST FAILED!")
        print("=" * 70)
        return False


if __name__ == "__main__":
    """Test violation reporter."""
    import sys
    
    try:
        success = test_violation_reporter()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
