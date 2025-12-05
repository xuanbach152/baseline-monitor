"""
System Information Module
=========================
Module thu thập thông tin hệ thống để đăng ký agent với backend.

Thông tin thu thập:
1. Hostname - Tên máy
2. IP Address - Địa chỉ IP (local và public)
3. OS Info - Hệ điều hành và phiên bản
4. MAC Address - Địa chỉ vật lý (để identify)
5. System Info - CPU, RAM, Disk
"""

import socket
import platform
import uuid
import psutil
from typing import Dict, Optional


def get_hostname() -> str:
   
    return socket.gethostname()


def get_local_ip() -> str:
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return '127.0.0.1'


def get_public_ip() -> Optional[str]:
    
    try:
        import urllib.request
        
        # Gọi API ipify để lấy public IP
        response = urllib.request.urlopen('https://api.ipify.org', timeout=3)
        public_ip = response.read().decode('utf-8')
        
        return public_ip
    except Exception:
        return None


def get_os_info() -> str:
    
    system = platform.system()
    
    if system == "Linux":
        
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('PRETTY_NAME'):
                        
                        distro = line.split('=')[1].strip().strip('"')
                        return distro
        except FileNotFoundError:
            pass
        
        
        return f"Linux {platform.release()}"
    
    elif system == "Windows":
        
        return platform.platform()
    
    elif system == "Darwin":
    
        return f"macOS {platform.mac_ver()[0]}"
    
    else:
        # Unknown OS
        return f"{system} {platform.release()}"


def get_mac_address() -> str:
    
    mac_num = uuid.getnode()
    mac_hex = ':'.join(('%012x' % mac_num)[i:i+2] for i in range(0, 12, 2))
    return mac_hex


def get_cpu_info() -> Dict[str, any]:
    
    try:
        return {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'frequency_mhz': int(psutil.cpu_freq().current) if psutil.cpu_freq() else 0
        }
    except Exception:
        return {}


def get_memory_info() -> Dict[str, any]:
    
    try:
        mem = psutil.virtual_memory()
        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_percent': mem.percent
        }
    except Exception:
        return {}


def get_disk_info() -> Dict[str, any]:
    
    try:
        disk = psutil.disk_usage('/')
        return {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'used_percent': disk.percent
        }
    except Exception:
        return {}


def get_agent_info(include_system_stats: bool = False) -> Dict[str, any]:
    
    info = {
        'hostname': get_hostname(),
        'ip_address': get_local_ip(),
        'os': get_os_info(),
        'mac_address': get_mac_address(),
        'version': '1.0.0'  
    }
    
    # Optional: Public IP
    public_ip = get_public_ip()
    if public_ip:
        info['public_ip'] = public_ip
    
    # Optional: System stats
    if include_system_stats:
        info['cpu'] = get_cpu_info()
        info['memory'] = get_memory_info()
        info['disk'] = get_disk_info()
    
    return info


if __name__ == "__main__":
    
    print("=" * 60)
    print("SYSTEM INFORMATION")
    print("=" * 60)
    
    print("\n Basic Info:")
    print(f"   Hostname:     {get_hostname()}")
    print(f"   Local IP:     {get_local_ip()}")
    print(f"   OS:           {get_os_info()}")
    print(f"   MAC Address:  {get_mac_address()}")
    
    print("\n Network:")
    public_ip = get_public_ip()
    if public_ip:
        print(f"   Public IP:    {public_ip}")
    else:
        print(f"   Public IP:    Unable to fetch")
    
    print("\n CPU:")
    cpu = get_cpu_info()
    if cpu:
        print(f"   Physical Cores: {cpu.get('physical_cores')}")
        print(f"   Logical Cores:  {cpu.get('logical_cores')}")
        print(f"   Usage:          {cpu.get('cpu_percent')}%")
        print(f"   Frequency:      {cpu.get('frequency_mhz')} MHz")
    
    print("\n Memory:")
    mem = get_memory_info()
    if mem:
        print(f"   Total:      {mem.get('total_gb')} GB")
        print(f"   Available:  {mem.get('available_gb')} GB")
        print(f"   Used:       {mem.get('used_percent')}%")
    
    print("\n Disk:")
    disk = get_disk_info()
    if disk:
        print(f"   Total:  {disk.get('total_gb')} GB")
        print(f"   Used:   {disk.get('used_gb')} GB ({disk.get('used_percent')}%)")
        print(f"   Free:   {disk.get('free_gb')} GB")
    
    print("\n" + "=" * 60)
    print(" Agent Registration Data:")
    print("=" * 60)
    
    agent_info = get_agent_info(include_system_stats=True)
    import json
    print(json.dumps(agent_info, indent=2))
    
    print("\n System info collected successfully!")
