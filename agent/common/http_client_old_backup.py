"""
HTTP Client Module
==================
HTTP client để agent giao tiếp với Backend API.
"""

from typing import Dict, List, Optional, Any
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from .logger import get_logger
    from .models import ViolationReport, Rule
except ImportError:
    # When running as __main__
    from logger import get_logger
    from models import ViolationReport, Rule


class BackendAPIClient:
    """HTTP Client để agent gọi Backend API."""
    
    def __init__(
        self,
        base_url: str,
        api_token: str,
        timeout: int = 30,
        retry_attempts: int = 3
    ):
        """
        Khởi tạo HTTP client.
        
        Args:
            base_url: Backend API base URL
            api_token: JWT token để authenticate
            timeout: Request timeout (seconds)
            retry_attempts: Số lần retry khi lỗi
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.timeout = timeout
        
        # Setup session với retry strategy
        self.session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=retry_attempts,
            backoff_factor=1,  # 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Logger
        self.logger = get_logger("http_client")
    
    def _get_headers(self) -> Dict[str, str]:
        """Trả về headers với JWT token."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "BaselineMonitor-Agent/1.0"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Gọi API và xử lý response.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body (JSON)
            params: Query parameters
            
        Returns:
            Response JSON as dict
            
        Raises:
            requests.RequestException: Nếu có lỗi
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.logger.debug(f"{method} {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            # Raise exception nếu status code lỗi
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout: {url}")
            raise
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {url} - {e}")
            raise
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {url} - {response.status_code}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {url} - {e}")
            raise
    
    # ==============================================
    # API METHODS
    # ==============================================
    
    def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Đăng ký agent với backend (hoặc update nếu đã tồn tại).
        
        POST /api/v1/agents/
        
        Args:
            agent_data: Dict chứa hostname, ip_address, os, version, etc.
            
        Returns:
            Dict với agent info (bao gồm id)
            
        Example:
            data = {
                "hostname": "dev-server",
                "ip_address": "192.168.1.100",
                "os": "Ubuntu 22.04",
                "version": "1.0.0",
                "mac_address": "00:11:22:33:44:55",
                "public_ip": "1.2.3.4",
                "cpu": {...},
                "memory": {...},
                "disk": {...}
            }
            result = client.register_agent(data)
            # result["id"] = agent_id
        """
        self.logger.info(f"Registering agent: {agent_data.get('hostname')}")
        return self._make_request("POST", "/api/v1/agents/", data=agent_data)
    
    def send_heartbeat(self, agent_id: int) -> Dict[str, Any]:
        """
        Gửi heartbeat để báo agent còn online.
        
        POST /api/v1/agents/heartbeat
        
        Args:
            agent_id: ID của agent
            
        Returns:
            Response dict
        """
        self.logger.debug(f"Sending heartbeat for agent {agent_id}")
        return self._make_request(
            "POST",
            "/api/v1/agents/heartbeat",
            data={"agent_id": agent_id}
        )
    
    def report_violations(
        self,
        agent_id: int,
        violations: List[ViolationReport]
    ) -> Dict[str, Any]:
        """
        Gửi violations lên backend.
        
        POST /api/v1/violations/
        
        Args:
            agent_id: ID của agent
            violations: List của ViolationReport objects
            
        Returns:
            Response dict với số lượng violations created
        """
        self.logger.info(f"Reporting {len(violations)} violations for agent {agent_id}")
        
        # Convert Pydantic models to dicts
        violations_data = [v.model_dump() for v in violations]
        
        return self._make_request(
            "POST",
            "/api/v1/violations/",
            data={"violations": violations_data}
        )
    
    def get_active_rules(self, os_type: str) -> List[Rule]:
        """
        Lấy danh sách rules active cho OS type.
        
        GET /api/v1/rules/active?os_type=ubuntu
        
        Args:
            os_type: OS type (ubuntu hoặc windows)
            
        Returns:
            List của Rule objects
        """
        self.logger.info(f"Fetching active rules for os_type={os_type}")
        
        response = self._make_request(
            "GET",
            "/api/v1/rules/active",
            params={"os_type": os_type}
        )
        
        # Parse response to Rule objects
        rules = [Rule(**rule_data) for rule_data in response.get("rules", [])]
        self.logger.info(f"Fetched {len(rules)} active rules")
        
        return rules
    
    def get_agent_info(self, agent_id: int) -> Dict[str, Any]:
        """
        Lấy thông tin agent.
        
        GET /api/v1/agents/{agent_id}
        
        Args:
            agent_id: ID của agent
            
        Returns:
            Agent info dict
        """
        self.logger.debug(f"Fetching info for agent {agent_id}")
        return self._make_request("GET", f"/api/v1/agents/{agent_id}")


if __name__ == "__main__":
    """Test HTTP client (cần backend chạy)."""
    print("=" * 60)
    print("🧪 TESTING BackendAPIClient")
    print("=" * 60)
    
    # Setup
    client = BackendAPIClient(
        base_url="http://localhost:8000",
        api_token="your-jwt-token-here",
        timeout=10
    )
    
    print("\n✅ Client initialized")
    print(f"   Base URL: {client.base_url}")
    print(f"   Timeout: {client.timeout}s")
    
    # Test basic request (sẽ fail nếu backend không chạy)
    print("\n⚠️  To test API calls, start backend server first:")
    print("   cd backend && uvicorn app.main:app --reload")
    
    print("\n" + "=" * 60)
    print("✅ HTTP CLIENT INITIALIZED")
    print("=" * 60)
