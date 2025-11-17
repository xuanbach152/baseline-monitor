
import os
import socket
import json
from pathlib import Path
from typing import Optional
import yaml


class AgentConfig:
    
    
    def __init__(self, config_path: str = "config.yaml"):
        
        self.config_path = Path(config_path)
        self._config_data = {}
        self._cache_file = Path(".agent_cache.json")
        self._cached_agent_id = None
        
        self._load_config()
        self._load_cache()
    
    def _load_config(self):

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate config structure."""
        required = ['agent', 'backend', 'scanner']
        for section in required:
            if section not in self._config_data:
                raise ValueError(f"Missing section: {section}")
        
      
        if not self._config_data['agent'].get('hostname'):
            self._config_data['agent']['hostname'] = socket.gethostname()
        
        
        os_type = self._config_data['agent'].get('os_type')
        if not os_type:
            raise ValueError("agent.os_type is required")
        if os_type not in ['ubuntu', 'windows']:
            raise ValueError(f"os_type must be 'ubuntu' or 'windows', got '{os_type}'")
        
      
        if not self._config_data['backend'].get('api_url'):
            raise ValueError("backend.api_url is required")
        
        # Validate scanner
        if not self._config_data['scanner'].get('rules_path'):
            raise ValueError("scanner.rules_path is required")
    
    def _load_cache(self):
        """Load agent_id từ cache."""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, 'r') as f:
                    cache = json.load(f)
                    self._cached_agent_id = cache.get('agent_id')
            except (json.JSONDecodeError, IOError):
                self._cached_agent_id = None
        else:
            self._cached_agent_id = None
    
    def save_agent_id(self, agent_id: int):
        """Lưu agent_id vào cache."""
        self._cached_agent_id = agent_id
        try:
            with open(self._cache_file, 'w') as f:
                json.dump({'agent_id': agent_id}, f)
        except IOError as e:
            print(f" Warning: Could not save cache: {e}")
    
    # Agent properties
    @property
    def agent_id(self) -> Optional[int]:
        """Agent ID từ cache (None nếu chưa đăng ký)."""
        return self._cached_agent_id
    
    @property
    def hostname(self) -> str:
        """Hostname (auto-detect nếu không có)."""
        return self._config_data['agent']['hostname']
    
    @property
    def agent_name(self) -> str:
        """Tên hiển thị."""
        return self._config_data['agent'].get('name', 'Unknown Agent')
    
    @property
    def os_type(self) -> str:
        """OS type: ubuntu hoặc windows."""
        return self._config_data['agent']['os_type']
    
    # Backend properties
    @property
    def api_url(self) -> str:
        """Backend API URL."""
        return self._config_data['backend']['api_url']
    
    @property
    def api_token(self) -> str:
        """JWT token (env var override)."""
        return os.getenv('AGENT_API_TOKEN') or \
               self._config_data['backend'].get('api_token', '')
    
    @property
    def api_timeout(self) -> int:
        """API request timeout."""
        return self._config_data['backend'].get('timeout', 30)
    
    @property
    def api_retry_attempts(self) -> int:
        """API retry attempts."""
        return self._config_data['backend'].get('retry_attempts', 3)
    
    # Scanner properties
    @property
    def scan_interval(self) -> int:
        """Scan interval (seconds)."""
        return self._config_data['scanner'].get('scan_interval', 3600)
    
    @property
    def rules_path(self) -> str:
        """Rules JSON file path."""
        return self._config_data['scanner']['rules_path']
    
    @property
    def command_timeout(self) -> int:
        """Command timeout."""
        return self._config_data['scanner'].get('command_timeout', 10)
    
    @property
    def report_pass_results(self) -> bool:
        """Report PASS results."""
        return self._config_data['scanner'].get('report_pass_results', False)
    
    # Logging properties
    @property
    def log_level(self) -> str:
        """Log level."""
        return self._config_data.get('logging', {}).get('level', 'INFO')
    
    @property
    def log_file(self) -> str:
        """Log file path."""
        return self._config_data.get('logging', {}).get('log_file', './logs/agent.log')
    
    @property
    def log_max_bytes(self) -> int:
        """Log file max size."""
        return self._config_data.get('logging', {}).get('max_bytes', 10485760)
    
    @property
    def log_backup_count(self) -> int:
        """Log backup count."""
        return self._config_data.get('logging', {}).get('backup_count', 5)
    
    @property
    def log_console_output(self) -> bool:
        """Log to console."""
        return self._config_data.get('logging', {}).get('console_output', True)


# Singleton
_config_instance: Optional[AgentConfig] = None

def get_config(config_path: str = "config.yaml") -> AgentConfig:
    """Get singleton config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = AgentConfig(config_path)
    return _config_instance


if __name__ == "__main__":
    """Test config."""
    import sys
    
    print("=" * 60)
    print(" TESTING AgentConfig")
    print("=" * 60)
    
    try:
        config = AgentConfig("config.yaml")
        print("\n Config loaded successfully!")
        
        print("\n Agent:")
        print(f"   Hostname:   {config.hostname}")
        print(f"   Name:       {config.agent_name}")
        print(f"   OS Type:    {config.os_type}")
        print(f"   Agent ID:   {config.agent_id or 'Not registered yet'}")
        
        print("\n Backend:")
        print(f"   API URL:    {config.api_url}")
        print(f"   Timeout:    {config.api_timeout}s")
        
        print("\n Scanner:")
        print(f"   Interval:   {config.scan_interval}s")
        print(f"   Rules:      {config.rules_path}")
        
        print("\n Logging:")
        print(f"   Level:      {config.log_level}")
        print(f"   File:       {config.log_file}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
