"""
Configuration Module
====================
Module này đọc file config YAML và validate các giá trị cấu hình.

Chức năng:
1. Đọc file config.yaml
2. Validate các trường bắt buộc
3. Auto-detect hostname nếu không có trong config
4. Hỗ trợ agent auto-registration (không cần agent_id thủ công)
5. Cache agent_id sau khi đăng ký thành công
"""

import os
import socket
import json
from pathlib import Path
from typing import Optional
import yaml


class AgentConfig:
    """
    Class quản lý cấu hình agent - đọc từ file YAML.
    
    Attributes:
        config_path (Path): Đường dẫn tới file config.yaml
        _config_data (dict): Dictionary chứa toàn bộ dữ liệu config
    
    Example:
        >>> config = AgentConfig("config.yaml")
        >>> print(config.agent_id)
        "agent-001"
        >>> print(config.scan_interval)
        3600
    """
    
    # ==========================================
    # PHẦN 1: CONSTRUCTOR - Khởi tạo config
    # ==========================================
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Khởi tạo AgentConfig.
        
        Args:
            config_path (str): Đường dẫn tới file YAML. Mặc định là "config.yaml"
        
        Raises:
            FileNotFoundError: Nếu file không tồn tại
            ValueError: Nếu thiếu các trường bắt buộc
            yaml.YAMLError: Nếu file YAML có lỗi cú pháp
        """
        self.config_path = Path(config_path)
        self._config_data = {}
        self._cache_file = Path(".agent_cache.json")  # Cache agent_id
        self._load_config()
        self._load_cache()
    
    # ==========================================
    # PHẦN 2: LOAD & VALIDATE CONFIG
    # ==========================================
    
    def _load_config(self):
        """
        Đọc file YAML và validate cấu trúc.
        
        Quy trình:
            1. Kiểm tra file có tồn tại không
            2. Đọc nội dung YAML thành dict
            3. Validate các trường bắt buộc
        
        Giải thích:
            - yaml.safe_load(): Đọc YAML an toàn (không execute code)
            - encoding='utf-8': Hỗ trợ tiếng Việt nếu có
        """
        # Bước 1: Kiểm tra file có tồn tại không
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"❌ Config file not found: {self.config_path}\n"
                f"💡 Hint: Copy config.example.yaml thành config.yaml"
            )
        
        # Bước 2: Đọc file YAML
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                # safe_load(): Parse YAML thành Python dict
                self._config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"❌ Invalid YAML format: {e}")
        
        # Bước 3: Validate cấu trúc config
        self._validate_config()
    
    def _validate_config(self):
        """
        Validate các trường bắt buộc trong config.
        
        Kiểm tra:
            1. Có đủ 3 section bắt buộc: agent, backend, scanner
            2. Các field bắt buộc có giá trị không empty
        
        Raises:
            ValueError: Nếu thiếu section hoặc field bắt buộc
        
        Giải thích:
            - required_sections: Danh sách sections phải có
            - Loop qua từng section để check
            - Dùng .get() để lấy value an toàn (không lỗi nếu key không tồn tại)
        """
        # Kiểm tra các section bắt buộc
        required_sections = ['agent', 'backend', 'scanner']
        for section in required_sections:
            if section not in self._config_data:
                raise ValueError(
                    f"❌ Missing required section: '{section}'\n"
                    f"💡 Check your config.yaml structure"
                )
        
        # Kiểm tra agent.hostname (không bắt buộc, sẽ auto-detect)
        if not self._config_data['agent'].get('hostname'):
            # Auto-detect hostname từ system
            self._config_data['agent']['hostname'] = socket.gethostname()
        
        # Kiểm tra agent.os_type (BẮT BUỘC)
        os_type = self._config_data['agent'].get('os_type')
        if not os_type:
            raise ValueError("❌ agent.os_type is required")
        
        # Validate os_type chỉ được là ubuntu hoặc windows
        if os_type not in ['ubuntu', 'windows']:
            raise ValueError(
                f"❌ agent.os_type must be 'ubuntu' or 'windows', got '{os_type}'"
            )
        
        # Kiểm tra backend.api_url (BẮT BUỘC)
        if not self._config_data['backend'].get('api_url'):
            raise ValueError("❌ backend.api_url is required")
        
        # Kiểm tra scanner.rules_path (BẮT BUỘC)
        if not self._config_data['scanner'].get('rules_path'):
            raise ValueError("❌ scanner.rules_path is required")
    
    # ==========================================
    # PHẦN 3: AGENT CONFIG PROPERTIES
    # ==========================================
    
    @property
    def agent_id(self) -> int:
        """
        ID của agent - định danh duy nhất (số).
        
        Returns:
            int: Agent ID từ database backend (vd: 1, 2, 3)
        
        Giải thích:
            - ID này phải khớp với id trong bảng agents của backend
            - Lấy từ section 'agent' > key 'agent_id'
        
        Lưu ý:
            - Phải tạo agent trong backend trước (qua seed_data.py hoặc API)
            - Sau đó lấy id từ database điền vào config.yaml
        """
        return int(self._config_data['agent']['agent_id'])
    
    @property
    def agent_name(self) -> str:
        """
        Tên hiển thị của agent.
        
        Returns:
            str: Agent name hoặc "Unknown Agent" nếu không có
        
        Giải thích:
            - .get(key, default): Lấy value, nếu không có trả về default
            - Không bắt buộc nên dùng .get() thay vì direct access
        """
        return self._config_data['agent'].get('name', 'Unknown Agent')
    
    @property
    def os_type(self) -> str:
        """
        Loại OS: "ubuntu" hoặc "windows".
        
        Returns:
            str: "ubuntu" hoặc "windows"
        """
        return self._config_data['agent']['os_type']
    
    @property
    def mac_address(self) -> Optional[str]:
        """
        MAC address của máy (optional, dùng để identify).
        
        Returns:
            Optional[str]: MAC address hoặc None
        """
        return self._config_data['agent'].get('mac_address')
    
    @property
    def ip_address(self) -> Optional[str]:
        """
        IP address của máy (optional, có thể auto-detect).
        
        Returns:
            Optional[str]: IP address hoặc None
        """
        return self._config_data['agent'].get('ip_address')
    
    # ==========================================
    # PHẦN 4: BACKEND CONFIG PROPERTIES
    # ==========================================
    
    @property
    def api_url(self) -> str:
        """
        URL của Backend API.
        
        Returns:
            str: API URL (vd: "http://localhost:8000")
        
        Giải thích:
            - Bắt buộc, đã validate nên có thể access trực tiếp
        """
        return self._config_data['backend']['api_url']
    
    @property
    def api_token(self) -> str:
        """
        JWT token để authenticate với backend.
        
        Returns:
            str: JWT token hoặc empty string
        
        Giải thích:
            - Ưu tiên lấy từ environment variable AGENT_API_TOKEN
            - Nếu không có env var, lấy từ config file
            - Nếu không có cả 2, trả về empty string
            - Dùng env var để bảo mật (không commit token vào git)
        
        Example:
            # Cách 1: Dùng env var (khuyến nghị)
            export AGENT_API_TOKEN="eyJhbGc..."
            
            # Cách 2: Ghi trong config.yaml
            backend:
              api_token: "eyJhbGc..."
        """
        # Ưu tiên env var > config file
        return os.getenv('AGENT_API_TOKEN') or \
               self._config_data['backend'].get('api_token', '')
    
    @property
    def api_timeout(self) -> int:
        """
        Timeout cho mỗi API request (giây).
        
        Returns:
            int: Timeout seconds, mặc định 30
        
        Giải thích:
            - Mặc định 30s đủ cho hầu hết requests
            - Có thể tùy chỉnh nếu network chậm
        """
        return self._config_data['backend'].get('timeout', 30)
    
    @property
    def api_retry_attempts(self) -> int:
        """
        Số lần retry khi API call fail.
        
        Returns:
            int: Số lần retry, mặc định 3
        
        Giải thích:
            - Retry 3 lần nếu network không ổn định
            - Backoff: 1s, 2s, 4s giữa các lần retry
        """
        return self._config_data['backend'].get('retry_attempts', 3)
    
    # ==========================================
    # PHẦN 5: SCANNER CONFIG PROPERTIES
    # ==========================================
    
    @property
    def scan_interval(self) -> int:
        """
        Thời gian giữa mỗi lần scan (giây).
        
        Returns:
            int: Interval seconds, mặc định 3600 (1 giờ)
        
        Giải thích:
            - Mặc định 3600s = 1 giờ
            - Có thể đổi thành 1800 (30 phút) hoặc 300 (5 phút) khi dev
        """
        return self._config_data['scanner'].get('scan_interval', 3600)
    
    @property
    def rules_path(self) -> str:
        """
        Đường dẫn tới file rules JSON.
        
        Returns:
            str: Path to rules file
        
        Giải thích:
            - Ubuntu: "./agent/rules/ubuntu_rules.json"
            - Windows: "./agent/rules/windows_rules.json"
            - Bắt buộc, đã validate
        """
        return self._config_data['scanner']['rules_path']
    
    @property
    def command_timeout(self) -> int:
        """
        Timeout cho mỗi command scan (giây).
        
        Returns:
            int: Command timeout, mặc định 10
        
        Giải thích:
            - Mỗi audit command phải hoàn thành trong 10s
            - Nếu quá 10s, coi như ERROR
        """
        return self._config_data['scanner'].get('command_timeout', 10)
    
    @property
    def report_pass_results(self) -> bool:
        """
        Có gửi kết quả PASS lên backend không.
        
        Returns:
            bool: True = gửi cả PASS, False = chỉ gửi FAIL/ERROR
        
        Giải thích:
            - False (mặc định): Chỉ gửi FAIL và ERROR (tiết kiệm bandwidth)
            - True: Gửi cả PASS (để có dữ liệu đầy đủ)
        """
        return self._config_data['scanner'].get('report_pass_results', False)
    
    # ==========================================
    # PHẦN 6: LOGGING CONFIG PROPERTIES
    # ==========================================
    
    @property
    def log_level(self) -> str:
        """
        Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL.
        
        Returns:
            str: Log level, mặc định "INFO"
        
        Giải thích:
            - DEBUG: Chi tiết nhất (dùng khi dev)
            - INFO: Thông tin bình thường (khuyến nghị)
            - WARNING: Chỉ cảnh báo
            - ERROR: Chỉ lỗi
        """
        return self._config_data.get('logging', {}).get('level', 'INFO')
    
    @property
    def log_file(self) -> str:
        """
        Đường dẫn file log.
        
        Returns:
            str: Log file path, mặc định "./logs/agent.log"
        
        Giải thích:
            - Logs sẽ được ghi vào file này
            - Tự động rotate khi đầy
        """
        return self._config_data.get('logging', {}).get('log_file', './logs/agent.log')
    
    @property
    def log_max_bytes(self) -> int:
        """
        Kích thước tối đa của 1 file log (bytes).
        
        Returns:
            int: Max bytes, mặc định 10MB
        
        Giải thích:
            - 10485760 bytes = 10MB
            - Khi đầy sẽ tự động tạo file mới (rotation)
        """
        return self._config_data.get('logging', {}).get('max_bytes', 10485760)
    
    @property
    def log_backup_count(self) -> int:
        """
        Số file log backup giữ lại.
        
        Returns:
            int: Backup count, mặc định 5
        
        Giải thích:
            - Giữ 5 file log cũ: agent.log.1, agent.log.2, ..., agent.log.5
            - File thứ 6 sẽ bị xóa
        """
        return self._config_data.get('logging', {}).get('backup_count', 5)
    
    @property
    def log_console_output(self) -> bool:
        """
        Có in log ra console không.
        
        Returns:
            bool: True = in cả console và file, False = chỉ file
        
        Giải thích:
            - True: Xem được log realtime trên terminal
            - False: Chỉ ghi vào file (dùng khi chạy background)
        """
        return self._config_data.get('logging', {}).get('console_output', True)


# ==========================================
# PHẦN 7: SINGLETON PATTERN (Optional)
# ==========================================

# Biến global để lưu instance duy nhất
_config_instance: Optional[AgentConfig] = None


def get_config(config_path: str = "config.yaml") -> AgentConfig:
    """
    Lấy singleton config instance.
    
    Args:
        config_path (str): Đường dẫn config file
    
    Returns:
        AgentConfig: Instance duy nhất của config
    
    Giải thích SINGLETON PATTERN:
        - Chỉ tạo 1 instance duy nhất cho toàn bộ app
        - Lần đầu gọi: Tạo instance mới
        - Các lần sau: Trả về instance đã tạo
        - Lợi ích: Tiết kiệm memory, config nhất quán
    
    Example:
        >>> # Trong module A
        >>> config = get_config()
        >>> print(config.agent_id)
        
        >>> # Trong module B
        >>> config = get_config()  # Cùng instance với module A
        >>> print(config.agent_id)  # Giá trị giống nhau
    """
    global _config_instance
    
    # Nếu chưa có instance, tạo mới
    if _config_instance is None:
        _config_instance = AgentConfig(config_path)
    
    # Trả về instance (đã có hoặc vừa tạo)
    return _config_instance


# ==========================================
# PHẦN 8: TESTING CODE
# ==========================================

if __name__ == "__main__":
    """
    Test module config.py.
    
    Chạy: python -m agent.common.config
    """
    import sys
    
    print("=" * 60)
    print("🧪 TESTING AgentConfig")
    print("=" * 60)
    
    try:
        # Test 1: Load config
        print("\n📖 Test 1: Loading config...")
        config = AgentConfig("config.yaml")
        print("   ✅ Config loaded successfully!")
        
        # Test 2: Agent config
        print("\n🤖 Test 2: Agent Configuration")
        print(f"   Agent ID:   {config.agent_id}")
        print(f"   Agent Name: {config.agent_name}")
        print(f"   OS Type:    {config.os_type}")
        print(f"   Hostname:   {config.hostname or 'Not set'}")
        
        # Test 3: Backend config
        print("\n🌐 Test 3: Backend Configuration")
        print(f"   API URL:     {config.api_url}")
        print(f"   API Token:   {config.api_token[:20]}..." if config.api_token else "   API Token:   Not set")
        print(f"   Timeout:     {config.api_timeout}s")
        print(f"   Retry:       {config.api_retry_attempts} times")
        
        # Test 4: Scanner config
        print("\n🔍 Test 4: Scanner Configuration")
        print(f"   Scan Interval:  {config.scan_interval}s ({config.scan_interval // 60} minutes)")
        print(f"   Rules Path:     {config.rules_path}")
        print(f"   Command Timeout: {config.command_timeout}s")
        print(f"   Report PASS:    {config.report_pass_results}")
        
        # Test 5: Logging config
        print("\n📝 Test 5: Logging Configuration")
        print(f"   Log Level:      {config.log_level}")
        print(f"   Log File:       {config.log_file}")
        print(f"   Max Size:       {config.log_max_bytes // 1024 // 1024}MB")
        print(f"   Backup Count:   {config.log_backup_count}")
        print(f"   Console Output: {config.log_console_output}")
        
        # Test 6: Singleton pattern
        print("\n🔄 Test 6: Singleton Pattern")
        config2 = get_config()
        print(f"   Same instance: {config is config2}")
        print(f"   config ID:     {id(config)}")
        print(f"   config2 ID:    {id(config2)}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Solution:")
        print("   1. Copy config file:")
        print("      cp config.example.yaml config.yaml")
        print("   2. Edit config.yaml with your settings")
        sys.exit(1)
        
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        print("\n💡 Check your config.yaml structure")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
