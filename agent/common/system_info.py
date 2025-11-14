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
    """
    Lấy hostname của máy.
    
    Returns:
        str: Hostname (vd: "web-server-01")
    
    Example:
        >>> get_hostname()
        'ubuntu-desktop'
    """
    return socket.gethostname()


def get_local_ip() -> str:
    """
    Lấy IP address local của máy (trong mạng LAN).
    
    Returns:
        str: IP address (vd: "192.168.1.10")
    
    Giải thích:
        - Tạo UDP socket
        - Connect tới external IP (không thực sự gửi data)
        - Lấy IP address của socket
        - Đây là IP mà máy dùng để ra internet
    
    Example:
        >>> get_local_ip()
        '192.168.1.10'
    """
    try:
        # Tạo UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Connect tới Google DNS (8.8.8.8)
        # Không thực sự gửi data, chỉ để OS chọn interface
        s.connect(('8.8.8.8', 80))
        
        # Lấy IP của socket
        local_ip = s.getsockname()[0]
        
        s.close()
        return local_ip
    except Exception:
        # Fallback nếu lỗi
        return '127.0.0.1'


def get_public_ip() -> Optional[str]:
    """
    Lấy IP address public (IP ra internet).
    
    Returns:
        Optional[str]: Public IP hoặc None nếu không lấy được
    
    Giải thích:
        - Gọi API external để lấy IP public
        - Dùng khi cần biết IP thực của máy từ bên ngoài
    
    Example:
        >>> get_public_ip()
        '42.118.234.123'
    """
    try:
        import urllib.request
        
        # Gọi API ipify để lấy public IP
        response = urllib.request.urlopen('https://api.ipify.org', timeout=3)
        public_ip = response.read().decode('utf-8')
        
        return public_ip
    except Exception:
        # Không lấy được (không có internet hoặc timeout)
        return None


def get_os_info() -> str:
    """
    Lấy thông tin hệ điều hành.
    
    Returns:
        str: OS info (vd: "Ubuntu 22.04.3 LTS", "Windows 11 Pro")
    
    Giải thích:
        - platform.system(): Linux, Windows, Darwin (macOS)
        - platform.release(): Kernel version hoặc Windows version
        - platform.version(): Chi tiết version
    
    Example:
        >>> get_os_info()
        'Linux 5.15.0-91-generic #101-Ubuntu SMP'
    """
    system = platform.system()
    
    if system == "Linux":
        # Linux: Đọc /etc/os-release để lấy distro name
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('PRETTY_NAME'):
                        # PRETTY_NAME="Ubuntu 22.04.3 LTS"
                        distro = line.split('=')[1].strip().strip('"')
                        return distro
        except FileNotFoundError:
            pass
        
        # Fallback
        return f"Linux {platform.release()}"
    
    elif system == "Windows":
        # Windows: Dùng platform.platform()
        return platform.platform()
    
    elif system == "Darwin":
        # macOS
        return f"macOS {platform.mac_ver()[0]}"
    
    else:
        # Unknown OS
        return f"{system} {platform.release()}"


def get_mac_address() -> str:
    """
    Lấy MAC address của interface chính.
    
    Returns:
        str: MAC address (vd: "aa:bb:cc:dd:ee:ff")
    
    Giải thích:
        - uuid.getnode(): Lấy MAC address dạng số
        - Convert sang format aa:bb:cc:dd:ee:ff
    
    Example:
        >>> get_mac_address()
        'a1:b2:c3:d4:e5:f6'
    """
    mac_num = uuid.getnode()
    mac_hex = ':'.join(('%012x' % mac_num)[i:i+2] for i in range(0, 12, 2))
    return mac_hex


def get_cpu_info() -> Dict[str, any]:
    """
    Lấy thông tin CPU.
    
    Returns:
        Dict: CPU info (cores, threads, usage, frequency)
    
    Example:
        >>> get_cpu_info()
        {
            'physical_cores': 4,
            'logical_cores': 8,
            'cpu_percent': 25.5,
            'frequency_mhz': 2400
        }
    """
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
    """
    Lấy thông tin RAM.
    
    Returns:
        Dict: Memory info (total, available, percent)
    
    Example:
        >>> get_memory_info()
        {
            'total_gb': 16.0,
            'available_gb': 8.5,
            'used_percent': 46.9
        }
    """
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
    """
    Lấy thông tin Disk.
    
    Returns:
        Dict: Disk info (total, used, free, percent)
    
    Example:
        >>> get_disk_info()
        {
            'total_gb': 500.0,
            'used_gb': 250.0,
            'free_gb': 250.0,
            'used_percent': 50.0
        }
    """
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
    """
    Thu thập TẤT CẢ thông tin để đăng ký agent.
    
    Args:
        include_system_stats: Có include CPU/RAM/Disk stats không
    
    Returns:
        Dict: Đầy đủ thông tin agent
    
    Giải thích:
        - Gọi tất cả các hàm trên
        - Tổng hợp thành 1 dict
        - Dùng để gửi lên backend khi đăng ký
    
    Example:
        >>> info = get_agent_info()
        >>> print(info)
        {
            'hostname': 'web-server-01',
            'ip_address': '192.168.1.10',
            'public_ip': '42.118.234.123',
            'os': 'Ubuntu 22.04.3 LTS',
            'mac_address': 'aa:bb:cc:dd:ee:ff',
            'version': '1.0.0'
        }
    """
    info = {
        'hostname': get_hostname(),
        'ip_address': get_local_ip(),
        'os': get_os_info(),
        'mac_address': get_mac_address(),
        'version': '1.0.0'  # Agent version (hardcode hoặc từ config)
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


# ==========================================
# TESTING CODE
# ==========================================

if __name__ == "__main__":
    """Test system info module."""
    print("=" * 60)
    print("🖥️  SYSTEM INFORMATION")
    print("=" * 60)
    
    print("\n📋 Basic Info:")
    print(f"   Hostname:     {get_hostname()}")
    print(f"   Local IP:     {get_local_ip()}")
    print(f"   OS:           {get_os_info()}")
    print(f"   MAC Address:  {get_mac_address()}")
    
    print("\n🌐 Network:")
    public_ip = get_public_ip()
    if public_ip:
        print(f"   Public IP:    {public_ip}")
    else:
        print(f"   Public IP:    Unable to fetch")
    
    print("\n💻 CPU:")
    cpu = get_cpu_info()
    if cpu:
        print(f"   Physical Cores: {cpu.get('physical_cores')}")
        print(f"   Logical Cores:  {cpu.get('logical_cores')}")
        print(f"   Usage:          {cpu.get('cpu_percent')}%")
        print(f"   Frequency:      {cpu.get('frequency_mhz')} MHz")
    
    print("\n💾 Memory:")
    mem = get_memory_info()
    if mem:
        print(f"   Total:      {mem.get('total_gb')} GB")
        print(f"   Available:  {mem.get('available_gb')} GB")
        print(f"   Used:       {mem.get('used_percent')}%")
    
    print("\n💿 Disk:")
    disk = get_disk_info()
    if disk:
        print(f"   Total:  {disk.get('total_gb')} GB")
        print(f"   Used:   {disk.get('used_gb')} GB ({disk.get('used_percent')}%)")
        print(f"   Free:   {disk.get('free_gb')} GB")
    
    print("\n" + "=" * 60)
    print("📦 Agent Registration Data:")
    print("=" * 60)
    
    agent_info = get_agent_info(include_system_stats=True)
    import json
    print(json.dumps(agent_info, indent=2))
    
    print("\n✅ System info collected successfully!")
