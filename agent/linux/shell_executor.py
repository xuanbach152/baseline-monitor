#!/usr/bin/env python3
"""
Shell Executor Module

Module để execute shell commands cho audit rules.
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple


sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.common import get_logger


logger = get_logger(__name__)


def execute_command(
    cmd: str,
    timeout: int = 30,
    shell: bool = True
) -> Tuple[int, str, str]:
    
    logger.debug(f"Executing command: {cmd}")
    
    try:
        
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  
        )
        
        exit_code = result.returncode
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        
        if exit_code == 0:
            logger.debug(f"   Command succeeded (exit code: {exit_code})")
            if stdout:
                logger.debug(f"  Output: {stdout[:100]}{'...' if len(stdout) > 100 else ''}")
        else:
            logger.warning(f"   Command failed (exit code: {exit_code})")
            if stderr:
                logger.warning(f"  Error: {stderr[:100]}{'...' if len(stderr) > 100 else ''}")
        
        return exit_code, stdout, stderr
        
    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after {timeout}s"
        logger.error(f"    {error_msg}: {cmd}")
        return -1, "", error_msg
        
    except Exception as e:
        error_msg = f"Failed to execute command: {str(e)}"
        logger.error(f"   {error_msg}")
        logger.error(f"  Command: {cmd}")
        return -1, "", error_msg


def execute_command_with_sudo(
    cmd: str,
    timeout: int = 30
) -> Tuple[int, str, str]:
    
    if not cmd.strip().startswith('sudo'):
        cmd = f"sudo {cmd}"
    
    return execute_command(cmd, timeout=timeout)


def check_command_available(command: str) -> bool:
    
    exit_code, _, _ = execute_command(
        f"command -v {command}",
        timeout=5
    )
    return exit_code == 0


def test_shell_executor():

    print("=" * 60)
    print(" TESTING Shell Executor")
    print("=" * 60)
    
    tests = [
        {
            "name": "Simple echo command",
            "cmd": "echo 'Hello from shell executor'",
            "expect_success": True
        },
        {
            "name": "Check /etc/os-release",
            "cmd": "grep '^NAME=' /etc/os-release",
            "expect_success": True
        },
        {
            "name": "List current directory",
            "cmd": "ls -la | head -5",
            "expect_success": True
        },
        {
            "name": "Non-existent command",
            "cmd": "this_command_does_not_exist",
            "expect_success": False
        },
        {
            "name": "Check if grep is available",
            "cmd": "command -v grep",
            "expect_success": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for idx, test in enumerate(tests, 1):
        print(f"\n{'='*60}")
        print(f"Test {idx}/{len(tests)}: {test['name']}")
        print(f"Command: {test['cmd']}")
        print("-" * 60)
        
        exit_code, stdout, stderr = execute_command(test['cmd'], timeout=10)
        
        success = (exit_code == 0) == test['expect_success']
        
        if success:
            print(f" PASSED")
            passed += 1
        else:
            print(f" FAILED")
            failed += 1
        
        print(f"Exit code: {exit_code}")
        if stdout:
            print(f"Stdout: {stdout[:200]}{'...' if len(stdout) > 200 else ''}")
        if stderr:
            print(f"Stderr: {stderr[:200]}{'...' if len(stderr) > 200 else ''}")
 
    print(f"\n{'='*60}")
    print("Testing command availability check...")
    print("-" * 60)
    
    commands_to_check = ['grep', 'systemctl', 'ls', 'this_does_not_exist']
    for cmd in commands_to_check:
        available = check_command_available(cmd)
        status = " Available" if available else " Not available"
        print(f"  {cmd:<20} : {status}")
    
    
    print(f"\n{'='*60}")
    print(" TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(tests)}")
    print(f" Passed: {passed}")
    print(f" Failed: {failed}")
    
    if failed == 0:
        print("\n ALL TESTS PASSED!")
    else:
        print(f"\n {failed} test(s) failed")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    """Test shell executor."""
    import sys
    
    success = test_shell_executor()
    sys.exit(0 if success else 1)
