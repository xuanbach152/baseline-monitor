"""
HTTP Client Module
"""

import time
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from .models import ViolationReport, ScanResult

logger = logging.getLogger("agent")

class BackendAPIClient:
    """Client để giao tiếp với backend API."""
    
    def __init__(
        self,
        api_url: str,
        api_token: str,
        timeout: int = 30,
        retry_attempts: int = 3
    ):
       
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_token}' if api_token else ''
        }
    

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        
        url = f"{self.api_url}{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f" {method} {url} (attempt {attempt + 1}/{self.retry_attempts})")
                
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                
                if response.status_code == 200 or response.status_code == 201:
                    logger.debug(f" Success: {response.status_code}")
                    return response.json()
                
                elif response.status_code == 401:
                    logger.error("Authentication failed: Invalid token")
                    return None
                
                elif response.status_code == 404:
                    logger.error(f" Not found: {url}")
                    return None
                
                else:
                    logger.warning(f"  Status {response.status_code}: {response.text}")
                    
                    
                    if response.status_code >= 500:
                        if attempt < self.retry_attempts - 1:
                            wait_time = 2 ** attempt  
                            logger.info(f" Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                            continue
                    
                    return None
            
            except requests.exceptions.Timeout:
                logger.error(f" Timeout after {self.timeout}s")
                if attempt < self.retry_attempts - 1:
                    logger.info(" Retrying...")
                    time.sleep(1)
                    continue
                return None
            
            except requests.exceptions.ConnectionError:
                logger.error(" Connection error: Backend unreachable")
                if attempt < self.retry_attempts - 1:
                    logger.info(" Retrying in 3s...")
                    time.sleep(3)
                    continue
                return None
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        
        logger.error(f" Failed after {self.retry_attempts} attempts")
        return None
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """GET request helper."""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """POST request helper."""
        return self._make_request('POST', endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """PUT request helper."""
        return self._make_request('PUT', endpoint, data=data)
    
    def delete(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """DELETE request helper."""
        return self._make_request('DELETE', endpoint)
    

    def register_agent(
        self,
        hostname: str,
        ip_address: Optional[str] = None,
        os: Optional[str] = None,
        version: Optional[str] = None
    ) -> Optional[int]:
        
        logger.info(f" Registering agent: {hostname}")
        
        data = {
            'hostname': hostname,
            'ip_address': ip_address,
            'os': os,
            'version': version
        }
        
        response = self._make_request('POST', '/api/v1/agents', data=data)
        
        if response and 'id' in response:
            agent_id = response['id']
            logger.info(f" Agent registered successfully! ID: {agent_id}")
            return agent_id
        else:
            logger.error(" Failed to register agent")
            return None
    

    def send_heartbeat(self, agent_id: int) -> bool:
       
        logger.debug(f" Sending heartbeat for agent {agent_id}")
        
        heartbeat_data = {
            'is_online': True,
            'version': '1.0.0'
        }
        
        response = self._make_request(
            'POST',
            f'/api/v1/agents/{agent_id}/heartbeat',
            data=heartbeat_data
        )
        
        if response:
            logger.debug(" Heartbeat sent")
            return True
        else:
            logger.warning(" Failed to send heartbeat")
            return False
    

    def get_agent_info(self, agent_id: int) -> Optional[Dict[str, Any]]:
        
        logger.debug(f" Fetching agent info: {agent_id}")
        
        response = self._make_request('GET', f'/api/v1/agents/{agent_id}')
        
        if response:
            logger.debug("Agent info fetched")
            return response
        else:
            logger.warning(" Failed to fetch agent info")
            return None
    

    def get_active_rules(self, os_type: str) -> List[Dict[str, Any]]:
        
        logger.info(f" Fetching active rules for {os_type}")
        
        response = self._make_request(
            'GET',
            '/api/v1/rules',
            params={'os_type': os_type, 'is_active': True}
        )
        
        if response:
            rules_count = len(response)
            logger.info(f" Fetched {rules_count} active rules")
            return response
        else:
            logger.warning(" Failed to fetch rules")
            return []
    

    def report_violations(
        self,
        agent_id: int,
        violations: List[ViolationReport]
    ) -> bool:
        
        if not violations:
            logger.debug("No violations to report")
            return True
        
        logger.info(f" Reporting {len(violations)} violations for agent {agent_id}")
        
        # Convert Pydantic models sang dict
        violations_data = [v.model_dump() for v in violations]
        
        response = self._make_request(
            'POST',
            f'/api/v1/agents/{agent_id}/violations/bulk',
            data={'violations': violations_data}
        )
        
        if response:
            logger.info(" Violations reported successfully")
            return True
        else:
            logger.error(" Failed to report violations")
            return False
    

    def get_agent_violations(
        self,
        agent_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
       
        logger.debug(f" Fetching violations for agent {agent_id}")
        
        response = self._make_request(
            'GET',
            f'/api/v1/agents/{agent_id}/violations',
            params={'limit': limit}
        )
        
        if response:
            logger.debug(f" Fetched {len(response)} violations")
            return response
        else:
            logger.warning(" Failed to fetch violations")
            return []
    

    def health_check(self) -> bool:
        
        logger.debug(" Health check...")
        
        try:
            response = requests.get(
                f"{self.api_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(" Backend is healthy")
                return True
            else:
                logger.warning(f"  Backend returned {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f" Backend is down: {e}")
            return False


if __name__ == "__main__":
    """Test HTTP client."""
    import sys
    from .logger import setup_logger
    from .system_info import get_agent_info
    
    print("=" * 60)
    print(" TESTING BackendAPIClient")
    print("=" * 60)
    
    setup_logger(log_level="DEBUG", console_output=True)
    
    client = BackendAPIClient(
        api_url="http://localhost:8000",
        api_token="",  
        timeout=10,
        retry_attempts=2
    )
    
    print("\n  Testing health check:")
    if client.health_check():
        print("    Backend is healthy")
    else:
        print("    Backend is down")
        sys.exit(1)
    
    print("\n  Testing agent registration:")
    agent_data = get_agent_info()
    agent_id = client.register_agent(
        hostname=agent_data['hostname'],
        ip_address=agent_data['ip_address'],
        os=agent_data['os'],
        mac_address=agent_data['mac_address'],
        version=agent_data['version']
    )
    
    if agent_id:
        print(f"    Agent ID: {agent_id}")
    else:
        print("    Registration failed")
        sys.exit(1)
    
    print("\n  Testing heartbeat:")
    if client.send_heartbeat(agent_id):
        print("    Heartbeat sent")
    else:
        print("    Heartbeat failed")
    
    print("\n  Testing get active rules:")
    rules = client.get_active_rules(os_type="ubuntu")
    print(f"    Fetched {len(rules)} rules")
    
    print("\n  Testing report violations:")
    test_violations = [
        ViolationReport(
            agent_id=agent_id,
            rule_id="UBU-01",
            status="FAIL",
            details="Test violation",
            raw_output="test output"
        )
    ]
    
    if client.report_violations(agent_id, test_violations):
        print("    Violations reported")
    else:
        print("    Report failed")
    
    print("\n" + "=" * 60)
    print(" ALL HTTP CLIENT TESTS COMPLETED!")
    print("=" * 60)
