#!/usr/bin/env python3
"""
Rule Loader Module
==================
Module để đọc và parse Ubuntu CIS Benchmark rules từ JSON file.

Usage:
    from agent.linux.rule_loader import load_rules
    
    rules = load_rules("agent/rules/ubuntu_rules.json")
    print(f"Loaded {len(rules)} rules")
"""

import json
import sys
from pathlib import Path
from typing import List


sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.common.models import Rule, RuleSeverity
from agent.common import get_logger


logger = get_logger(__name__)


def load_rules(rules_path: str) -> List[Rule]:
    """
    Load CIS rules từ JSON file và parse thành list Rule objects.
    
    Args:
        rules_path: Path tới JSON file chứa rules (ví dụ: "agent/rules/ubuntu_rules.json")
    
    Returns:
        List[Rule]: Danh sách Rule objects đã được validate
    
    Raises:
        FileNotFoundError: Nếu file không tồn tại
        json.JSONDecodeError: Nếu JSON format không hợp lệ
        ValueError: Nếu rule data không hợp lệ
    
    Example:
        >>> rules = load_rules("agent/rules/ubuntu_rules.json")
        >>> print(f"Loaded {len(rules)} rules")
        Loaded 10 rules
    """
    # Validate file exists
    rules_file = Path(rules_path)
    if not rules_file.exists():
        error_msg = f"Rules file not found: {rules_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logger.info(f"Loading rules from: {rules_path}")
    
    try:
        # Read JSON file
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
        
        if not isinstance(rules_data, list):
            raise ValueError(f"Expected JSON array, got {type(rules_data).__name__}")
        
        logger.debug(f"Found {len(rules_data)} rules in JSON file")
        
        # Parse each rule
        rules = []
        for idx, rule_dict in enumerate(rules_data):
            try:
                rule = _parse_rule(rule_dict)
                rules.append(rule)
                logger.debug(f"  [{idx+1}/{len(rules_data)}]  {rule.rule_id}: {rule.title}")
            except Exception as e:
                logger.error(f"  [{idx+1}/{len(rules_data)}] Failed to parse rule: {e}")
                logger.error(f"  Rule data: {rule_dict}")
                # Continue parsing other rules instead of failing completely
                continue
        
        if not rules:
            raise ValueError("No valid rules found in file")
        
        logger.info(f" Successfully loaded {len(rules)} rules")
        return rules
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format in {rules_path}: {e}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Failed to load rules from {rules_path}: {e}"
        logger.error(error_msg)
        raise


def _parse_rule(rule_dict: dict) -> Rule:
    """
    Parse một rule dictionary thành Rule object.
    
    Mapping từ ubuntu_rules.json format sang Rule model:
    - id → rule_id
    - name → title
    - description → description
    - severity → severity (convert to enum)
    - audit_command → check_expression
    - remediation → remediation
    - expected_output → không map (sẽ dùng trong scanner)
    
    Args:
        rule_dict: Dictionary chứa rule data từ JSON
    
    Returns:
        Rule: Validated Rule object
    
    Raises:
        ValueError: Nếu required fields bị thiếu hoặc invalid
    """
    # Validate required fields
    required_fields = ['id', 'name', 'audit_command', 'severity']
    missing_fields = [f for f in required_fields if f not in rule_dict]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Map severity string to enum
    severity_map = {
        'low': RuleSeverity.LOW,
        'medium': RuleSeverity.MEDIUM,
        'high': RuleSeverity.HIGH,
        'critical': RuleSeverity.CRITICAL
    }
    
    severity_str = rule_dict['severity'].lower()
    if severity_str not in severity_map:
        raise ValueError(f"Invalid severity: {rule_dict['severity']}")
    
    severity = severity_map[severity_str]
    
    # Extract category from rule_id (UBU-01 → SSH, UBU-02 → Firewall, etc.)
    # For simplicity, we'll use "Security" as default category
    # You can enhance this mapping later
    category = _extract_category(rule_dict.get('name', ''))
    
    # Create Rule object
    rule = Rule(
        rule_id=rule_dict['id'],
        title=rule_dict['name'],
        description=rule_dict.get('description', ''),
        severity=severity,
        os_type='ubuntu',  # Hardcoded for Ubuntu rules
        category=category,
        check_expression=rule_dict['audit_command'],
        remediation=rule_dict.get('remediation', ''),
        is_active=True
    )
    
    return rule


def _extract_category(rule_name: str) -> str:
    """
    Extract category từ rule name.
    
    Simple keyword matching để determine category.
    
    Args:
        rule_name: Name của rule
    
    Returns:
        str: Category name
    """
    rule_name_lower = rule_name.lower()
    
    if 'ssh' in rule_name_lower:
        return 'SSH'
    elif 'firewall' in rule_name_lower or 'ufw' in rule_name_lower:
        return 'Firewall'
    elif 'audit' in rule_name_lower:
        return 'Auditing'
    elif 'update' in rule_name_lower:
        return 'System Updates'
    elif 'password' in rule_name_lower:
        return 'Password Policy'
    elif 'tmp' in rule_name_lower or 'mount' in rule_name_lower:
        return 'Filesystem'
    elif 'apparmor' in rule_name_lower or 'selinux' in rule_name_lower:
        return 'Access Control'
    elif 'log' in rule_name_lower or 'rsyslog' in rule_name_lower:
        return 'Logging'
    elif 'ipv6' in rule_name_lower or 'network' in rule_name_lower:
        return 'Network'
    else:
        return 'Security'


def validate_rules_file(rules_path: str) -> bool:
    """
    Validate rules file format mà không load vào memory.
    
    Useful để test file format trước khi deploy.
    
    Args:
        rules_path: Path tới JSON file
    
    Returns:
        bool: True nếu file valid, False nếu invalid
    """
    try:
        rules = load_rules(rules_path)
        print(f"Rules file is valid: {len(rules)} rules loaded")
        return True
    except Exception as e:
        print(f"Rules file is invalid: {e}")
        return False


if __name__ == "__main__":
    """Test rule loader."""
    print("=" * 60)
    print(" TESTING Rule Loader")
    print("=" * 60)
    
    # Test với ubuntu_rules.json
    rules_path = "agent/rules/ubuntu_rules.json"
    
    print(f"\nLoading rules from: {rules_path}")
    print("-" * 60)
    
    try:
        rules = load_rules(rules_path)
        
        print(f"\n Successfully loaded {len(rules)} rules")
        print("\n Rules Summary:")
        print("-" * 60)
        
        # Group by severity
        severity_counts = {}
        for rule in rules:
            severity_counts[rule.severity] = severity_counts.get(rule.severity, 0) + 1
        
        for severity, count in severity_counts.items():
            print(f"  {severity}: {count} rules")
        
        # Show details
        print("\n Detailed Rules:")
        print("-" * 60)
        for idx, rule in enumerate(rules, 1):
            print(f"\n{idx}. {rule.rule_id}: {rule.title}")
            print(f"   Severity: {rule.severity}")
            print(f"   Category: {rule.category}")
            print(f"   Check: {rule.check_expression[:50]}...")
        
        print("\n" + "=" * 60)
        print(" RULE LOADER TEST PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)