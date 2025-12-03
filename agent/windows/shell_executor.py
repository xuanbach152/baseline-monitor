#!/usr/bin/env python3
"""
Windows Shell/PowerShell Executor Module
=========================================
Module để execute PowerShell commands trên Windows và capture output.

Usage:
    from agent.windows.shell_executor import execute_command
    
    exit_code, stdout, stderr = execute_command("Get-Service -Name wuauserv")
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.common import get_logger

logger = get_logger(__name__)


def execute_command(
    cmd: str,
    timeout: int = 30,
    use_powershell: bool = True
) -> Tuple[int, str, str]:
    """
    Execute một command trên Windows (PowerShell hoặc CMD).
    
    Args:
        cmd: Command string cần execute
        timeout: Timeout in seconds (default: 30s)
        use_powershell: True = dùng PowerShell, False = dùng CMD
    
    Returns:
        Tuple[int, str, str]: (exit_code, stdout, stderr)
        - exit_code: 0 = success, != 0 = error, -1 = timeout/exception
        - stdout: Standard output text
        - stderr: Standard error text
    
    Example:
        >>> exit_code, stdout, stderr = execute_command("Get-Process")
        >>> if exit_code == 0:
        ...     print(f"Output: {stdout}")
    """
    logger.debug(f"Executing command: {cmd}")
    
    try:
        if use_powershell:
            # PowerShell command với UTF-8 encoding
            full_cmd = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                cmd
            ]
        else:
            # CMD command
            full_cmd = ["cmd.exe", "/c", cmd]
        
        # Execute command với timeout
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'  # Replace invalid chars instead of failing
        )
        
        exit_code = result.returncode
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        # Log result
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
        logger.error(f"   Command timeout after {timeout}s")
        return -1, "", f"Command timeout after {timeout} seconds"
        
    except FileNotFoundError as e:
        logger.error(f"   Command not found: {e}")
        return -1, "", f"Command not found: {str(e)}"
        
    except Exception as e:
        logger.error(f"   Command execution error: {e}", exc_info=True)
        return -1, "", f"Execution error: {str(e)}"


def test_shell_executor():
    """Test PowerShell executor với một số commands."""
    print("=" * 70)
    print(" TESTING Windows PowerShell Executor")
    print("=" * 70)
    
    test_commands = [
        # Basic test
        ("echo 'Hello from PowerShell'", "Test basic echo"),
        
        # Windows version
        ("(Get-WmiObject Win32_OperatingSystem).Caption", "Get Windows version"),
        
        # Service status
        ("Get-Service -Name wuauserv | Select-Object -ExpandProperty Status", "Check Windows Update service"),
        
        # Firewall status
        ("Get-NetFirewallProfile -Profile Domain | Select-Object -ExpandProperty Enabled", "Check Firewall status"),
        
        # UAC status
        ("Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' -Name EnableLUA | Select-Object -ExpandProperty EnableLUA", "Check UAC status"),
        
        # Invalid command (should fail gracefully)
        ("Get-InvalidCommand", "Test error handling"),
    ]
    
    print("\n Running test commands...")
    print("-" * 70)
    
    for idx, (cmd, description) in enumerate(test_commands, 1):
        print(f"\n[{idx}/{len(test_commands)}] {description}")
        print(f"Command: {cmd}")
        
        exit_code, stdout, stderr = execute_command(cmd, timeout=10)
        
        print(f"Exit code: {exit_code}")
        if stdout:
            print(f"Output: {stdout}")
        if stderr:
            print(f"Error: {stderr}")
        
        if exit_code == 0:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
    
    print("\n" + "=" * 70)
    print(" TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    """Test shell executor."""
    import platform
    
    if platform.system() != "Windows":
        print("⚠️  This module is designed for Windows only.")
        print(f"   Current OS: {platform.system()}")
        print("\n   You can still review the code, but execution will fail.")
        print("   To test, run this on a Windows machine.")
        sys.exit(1)
    
    try:
        test_shell_executor()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
