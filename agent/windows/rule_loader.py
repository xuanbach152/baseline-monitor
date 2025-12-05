#!/usr/bin/env python3
"""
Windows Rule Loader Module

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
 
    rules_file = Path(rules_path)
    if not rules_file.exists():
        error_msg = f"Rules file not found: {rules_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logger.info(f"Loading rules from: {rules_path}")
    
    try:
        
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
        
        if not isinstance(rules_data, list):
            raise ValueError(f"Expected JSON array, got {type(rules_data).__name__}")
        
        logger.debug(f"Found {len(rules_data)} rules in JSON file")
        
    
        rules = []
        for idx, rule_dict in enumerate(rules_data):
            try:
                rule = _parse_rule(rule_dict)
                rules.append(rule)
                logger.debug(f"  [{idx+1}/{len(rules_data)}]  {rule.rule_id}: {rule.title}")
            except Exception as e:
                logger.error(f"  [{idx+1}/{len(rules_data)}] Failed to parse rule: {e}")
                logger.error(f"  Rule data: {rule_dict}")
               
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
    
    """
   
    required_fields = ['id', 'name', 'audit_command', 'severity']
    missing_fields = [f for f in required_fields if f not in rule_dict]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
  
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
    
   
    category = _extract_category(rule_dict.get('name', ''))
    
    
    rule = Rule(
        rule_id=rule_dict['id'],
        title=rule_dict['name'],
        description=rule_dict.get('description', ''),
        severity=severity,
        os_type='windows',  
        category=category,
        check_expression=rule_dict['audit_command'],
        remediation=rule_dict.get('remediation', ''),
        is_active=True
    )
    
    return rule


def _extract_category(rule_name: str) -> str:
    """
    Extract category từ rule name.
   
    """
    rule_name_lower = rule_name.lower()
    
    if 'smb' in rule_name_lower or 'protocol' in rule_name_lower:
        return 'Network'
    elif 'defender' in rule_name_lower or 'antivirus' in rule_name_lower:
        return 'Antivirus'
    elif 'firewall' in rule_name_lower:
        return 'Firewall'
    elif 'password' in rule_name_lower or 'lockout' in rule_name_lower:
        return 'Password Policy'
    elif 'uac' in rule_name_lower or 'user account control' in rule_name_lower:
        return 'Access Control'
    elif 'audit' in rule_name_lower or 'logon' in rule_name_lower:
        return 'Auditing'
    elif 'remote desktop' in rule_name_lower or 'rdp' in rule_name_lower:
        return 'Network'
    elif 'update' in rule_name_lower:
        return 'System Updates'
    else:
        return 'Security'


def validate_rules_file(rules_path: str) -> bool:
    """
    Validate rules file format mà không load vào memory.
    """
    try:
        rules = load_rules(rules_path)
        print(f"Rules file is valid: {len(rules)} rules loaded")
        return True
    except Exception as e:
        print(f" Rules file is invalid: {e}")
        return False


if __name__ == "__main__":
    """Test rule loader."""
    print("=" * 70)
    print(" TESTING Windows Rule Loader")
    print("=" * 70)
    
   
    rules_path = "agent/rules/windows_rules.json"
    
    print(f"\nLoading rules from: {rules_path}")
    print("-" * 70)
    
    try:
        rules = load_rules(rules_path)
        
        print(f"\n Successfully loaded {len(rules)} rules")
        print("\n Rules Summary:")
        print("-" * 70)
        
     
        severity_counts = {}
        for rule in rules:
            severity_counts[rule.severity] = severity_counts.get(rule.severity, 0) + 1
        
        for severity, count in sorted(severity_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {severity}: {count} rules")
        
       
        print("\n Detailed Rules:")
        print("-" * 70)
        for idx, rule in enumerate(rules, 1):
            print(f"\n{idx}. {rule.rule_id}: {rule.title}")
            print(f"   Severity: {rule.severity}")
            print(f"   Category: {rule.category}")
            print(f"   Check: {rule.check_expression[:80]}...")
        
        print("\n" + "=" * 70)
        print(" RULE LOADER TEST PASSED!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
