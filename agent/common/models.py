"""
Data Models Module
==================
Pydantic models để validate dữ liệu agent.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class ViolationStatus(str, Enum):
    """Status của một violation."""
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class RuleSeverity(str, Enum):
    """Mức độ nghiêm trọng."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Rule(BaseModel):
    """Model đại diện cho một CIS rule."""
    rule_id: str = Field(..., description="Rule ID")
    title: str = Field(..., description="Tên rule")
    description: Optional[str] = Field(None, description="Mô tả chi tiết")
    severity: RuleSeverity = Field(..., description="Mức độ nghiêm trọng")
    os_type: str = Field(..., description="ubuntu hoặc windows")
    category: str = Field(..., description="Danh mục")
    check_expression: str = Field(..., description="Command để audit")
    remediation: Optional[str] = Field(None, description="Cách fix")
    is_active: bool = Field(True, description="Rule có active không")
    
    class Config:
        use_enum_values = True


class ViolationReport(BaseModel):
    """Model đại diện cho một violation report."""
    agent_id: int = Field(..., description="ID của agent")
    rule_id: str = Field(..., description="Rule bị vi phạm")
    status: ViolationStatus = Field(..., description="PASS/FAIL/ERROR")
    details: Optional[str] = Field(None, description="Chi tiết violation")
    detected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Thời điểm phát hiện"
    )
    raw_output: Optional[str] = Field(None, description="Output của audit command")
    
    class Config:
        use_enum_values = True


class ScanResult(BaseModel):
    """Model đại diện cho kết quả scan."""
    agent_id: int = Field(..., description="ID của agent")
    scan_started_at: datetime = Field(..., description="Thời điểm bắt đầu scan")
    scan_completed_at: Optional[datetime] = Field(None, description="Thời điểm kết thúc")
    total_rules_checked: int = Field(0, description="Tổng số rules đã check")
    violations: List[ViolationReport] = Field(
        default_factory=list,
        description="Danh sách violations"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Danh sách lỗi trong quá trình scan"
    )
    
    @property
    def pass_count(self) -> int:
        """Đếm số rules PASS."""
        return sum(1 for v in self.violations if v.status == ViolationStatus.PASS)
    
    @property
    def fail_count(self) -> int:
        """Đếm số rules FAIL."""
        return sum(1 for v in self.violations if v.status == ViolationStatus.FAIL)
    
    @property
    def error_count(self) -> int:
        """Đếm số rules ERROR."""
        return sum(1 for v in self.violations if v.status == ViolationStatus.ERROR)
    
    @property
    def compliance_rate(self) -> float:
        """Tính tỷ lệ tuân thủ (%)."""
        if self.total_rules_checked == 0:
            return 0.0
        return (self.pass_count / self.total_rules_checked) * 100
    
    def summary(self) -> str:
        """Tạo summary string."""
        return (
            f"Scan Result for Agent {self.agent_id}\n"
            f"  Total Rules: {self.total_rules_checked}\n"
            f"  ✅ Pass: {self.pass_count}\n"
            f"  ❌ Fail: {self.fail_count}\n"
            f"  ⚠️  Error: {self.error_count}\n"
            f"  📊 Compliance: {self.compliance_rate:.1f}%"
        )
    
    class Config:
        use_enum_values = True


class AgentStatus(BaseModel):
    """Model đại diện cho status của agent."""
    agent_id: int
    name: str
    os_type: str
    is_online: bool = True
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    last_scan_at: Optional[datetime] = None
    total_scans: int = 0
    current_compliance_rate: float = 0.0
    
    def update_heartbeat(self):
        """Cập nhật thời gian heartbeat."""
        self.last_heartbeat = datetime.utcnow()
        self.is_online = True
    
    def update_scan_result(self, result: ScanResult):
        """Cập nhật sau khi scan xong."""
        self.last_scan_at = result.scan_completed_at
        self.total_scans += 1
        self.current_compliance_rate = result.compliance_rate
    
    class Config:
        use_enum_values = True


if __name__ == "__main__":
    """Test models."""
    import json
    
    print("=" * 60)
    print("🧪 TESTING Models")
    print("=" * 60)
    
    # Test 1: Rule model
    print("\n1️⃣  Testing Rule model:")
    rule = Rule(
        rule_id="UBU-01",
        title="SSH Root Login Disabled",
        severity=RuleSeverity.HIGH,
        os_type="ubuntu",
        category="SSH",
        check_expression="grep '^PermitRootLogin' /etc/ssh/sshd_config",
        is_active=True
    )
    print(f"   ✅ Rule: {rule.rule_id} - {rule.title}")
    print(f"   Severity: {rule.severity}")
    
    # Test 2: ViolationReport model
    print("\n2️⃣  Testing ViolationReport model:")
    violation = ViolationReport(
        agent_id=1,
        rule_id="UBU-01",
        status=ViolationStatus.FAIL,
        details="PermitRootLogin is set to yes",
        raw_output="PermitRootLogin yes"
    )
    print(f"   ✅ Violation: {violation.rule_id} - {violation.status}")
    print(f"   Details: {violation.details}")
    
    # Test 3: ScanResult model
    print("\n3️⃣  Testing ScanResult model:")
    result = ScanResult(
        agent_id=1,
        scan_started_at=datetime.utcnow(),
        total_rules_checked=10
    )
    
    # Thêm violations
    for i in range(7):
        result.violations.append(ViolationReport(
            agent_id=1,
            rule_id=f"UBU-0{i+1}",
            status=ViolationStatus.PASS if i < 5 else ViolationStatus.FAIL,
            details=f"Check {i+1}"
        ))
    
    result.scan_completed_at = datetime.utcnow()
    print(f"\n{result.summary()}")
    
    # Test 4: JSON serialization
    print("\n4️⃣  Testing JSON serialization:")
    violation_dict = violation.model_dump()
    print(f"   ✅ Violation as dict:")
    print(f"   {json.dumps(violation_dict, indent=6, default=str)}")
    
    print("\n" + "=" * 60)
    print("✅ ALL MODEL TESTS PASSED!")
    print("=" * 60)
