# Agent Common Module

Module chứa các thành phần dùng chung cho cả Linux và Windows agent.

## 📂 Cấu Trúc

```
agent/common/
├── __init__.py         # Package init
├── config.py          # ⚙️ Configuration loader
├── logger.py          # 📝 Logging system
├── http_client.py     # 🌐 HTTP client cho backend API
├── models.py          # 📊 Pydantic data models
└── README.md          # 📖 Tài liệu này
```

## 🎯 Nhiệm Vụ Của Bạn

### 1. `config.py` - Configuration Loader (⏱️ 1 giờ)

**Mục tiêu:** Đọc file `config.yaml` và validate các giá trị.

**Checklist:**
- [ ] Tạo class `AgentConfig`
- [ ] Implement `__init__(config_path)` - Constructor
- [ ] Implement `_load_config()` - Đọc YAML file
- [ ] Implement `_validate_config()` - Validate required fields
- [ ] Tạo các `@property` để truy cập config dễ dàng
- [ ] (Optional) Hỗ trợ environment variables override
- [ ] Test với `config.example.yaml`

**Thư viện cần:**
```bash
pip install pyyaml pydantic
```

**Test:**
```bash
cd /home/bach/baseline-monitor
python -m agent.common.config
```

---

### 2. `logger.py` - Logging System (⏱️ 45 phút)

**Mục tiêu:** Tạo logger với file rotation và console output.

**Checklist:**
- [ ] Implement `setup_logger()` function
- [ ] Tạo `RotatingFileHandler` (auto-rotate khi file đầy)
- [ ] Tạo `StreamHandler` cho console output
- [ ] Format log message với timestamp
- [ ] Implement `get_logger()` helper
- [ ] Test log vào file `./logs/agent.log`

**Thư viện cần:** (Built-in Python)
```python
import logging
from logging.handlers import RotatingFileHandler
```

**Test:**
```bash
python -m agent.common.logger
ls -lh ./logs/  # Kiểm tra file log được tạo
```

---

### 3. `http_client.py` - HTTP Client (⏱️ 1.5 giờ)

**Mục tiêu:** HTTP client để agent gọi Backend API.

**Checklist:**
- [ ] Tạo class `BackendAPIClient`
- [ ] Setup `requests.Session` với retry strategy
- [ ] Implement `_get_headers()` - JWT authentication
- [ ] Implement `_make_request()` - Generic HTTP call
- [ ] Implement `send_heartbeat()` - POST /api/v1/agents/heartbeat
- [ ] Implement `report_violations()` - POST /api/v1/violations/
- [ ] Implement `get_active_rules()` - GET /api/v1/rules/active
- [ ] Implement `get_agent_info()` - GET /api/v1/agents/{id}
- [ ] Xử lý timeout và errors
- [ ] Test với backend đang chạy

**Thư viện cần:**
```bash
pip install requests
```

**Test:**
```bash
# 1. Start backend server
cd /home/bach/baseline-monitor/backend
uvicorn app.main:app --reload

# 2. Test HTTP client (tab mới)
cd /home/bach/baseline-monitor
python -m agent.common.http_client
```

---

### 4. `models.py` - Data Models (⏱️ 45 phút)

**Mục tiêu:** Tạo Pydantic models để validate dữ liệu.

**Checklist:**
- [ ] Định nghĩa `ViolationStatus` enum (PASS/FAIL/ERROR)
- [ ] Định nghĩa `RuleSeverity` enum (LOW/MEDIUM/HIGH/CRITICAL)
- [ ] Implement `Rule` model
- [ ] Implement `ViolationReport` model
- [ ] Implement `ScanResult` model (với properties: pass_count, fail_count, compliance_rate)
- [ ] Implement `AgentStatus` model
- [ ] Test serialize/deserialize JSON

**Thư viện cần:**
```bash
pip install pydantic
```

**Test:**
```bash
python -m agent.common.models
```

---

## 🧪 Testing Workflow

### Bước 1: Test từng module riêng lẻ

```bash
cd /home/bach/baseline-monitor

# Test config
python -m agent.common.config

# Test logger
python -m agent.common.logger

# Test models
python -m agent.common.models

# Test HTTP client (cần backend chạy)
python -m agent.common.http_client
```

### Bước 2: Test tích hợp tất cả modules

Tạo file `test_integration.py`:

```python
# agent/common/test_integration.py
from agent.common.config import AgentConfig
from agent.common.logger import setup_logger
from agent.common.http_client import BackendAPIClient
from agent.common.models import ViolationReport, ViolationStatus

def test_integration():
    print("=== Integration Test ===\n")
    
    # 1. Load config
    config = AgentConfig("config.yaml")
    print(f"✅ Config loaded: {config.agent_id}")
    
    # 2. Setup logger
    logger = setup_logger(
        name="test",
        log_file=config.log_file,
        log_level=config.log_level
    )
    logger.info("✅ Logger initialized")
    
    # 3. Create HTTP client
    client = BackendAPIClient(
        base_url=config.api_url,
        api_token=config.api_token
    )
    logger.info("✅ HTTP client created")
    
    # 4. Test heartbeat
    result = client.send_heartbeat(config.agent_id)
    logger.info(f"✅ Heartbeat OK: {result}")
    
    # 5. Test violation report
    violation = ViolationReport(
        agent_id=config.agent_id,
        rule_id="TEST-01",
        status=ViolationStatus.PASS,
        details="Integration test"
    )
    logger.info(f"✅ Violation created: {violation.dict()}")
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_integration()
```

Chạy test:
```bash
python agent/common/test_integration.py
```

---

## 📚 Tài Liệu Tham Khảo

### Config với PyYAML
```python
import yaml

with open('config.yaml', 'r') as f:
    data = yaml.safe_load(f)

agent_id = data['agent']['agent_id']
```

### Logging với Rotation
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### HTTP với Retry
```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
```

### Pydantic Models
```python
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## ⏰ Thời Gian Ước Tính

| Module | Thời gian | Độ khó |
|--------|-----------|---------|
| `config.py` | 1h | ⭐⭐ |
| `logger.py` | 45min | ⭐ |
| `models.py` | 45min | ⭐⭐ |
| `http_client.py` | 1h 30min | ⭐⭐⭐ |
| **TỔNG** | **4h** | |

---

## ✅ Checklist Hoàn Thành

Sau khi xong, check các điều sau:

- [ ] Tất cả 4 modules đã implement xong
- [ ] Test từng module riêng lẻ đều pass
- [ ] Integration test pass
- [ ] `config.yaml` được tạo và validate OK
- [ ] Log files xuất hiện trong `./logs/`
- [ ] HTTP client connect được với backend
- [ ] Models serialize/deserialize JSON đúng
- [ ] Code có comments và docstrings đầy đủ

---

## 🆘 Hỗ Trợ

Nếu gặp vấn đề:

1. **ImportError:** Cài đặt dependencies
   ```bash
   pip install pyyaml pydantic requests
   ```

2. **FileNotFoundError:** Tạo file config
   ```bash
   cp config.example.yaml config.yaml
   # Chỉnh sửa config.yaml với thông tin thật
   ```

3. **Connection Error:** Đảm bảo backend đang chạy
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. **JWT Token Invalid:** Lấy token mới
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

---

## 🎯 Next Steps (Day 2)

Sau khi hoàn thành Agent Core, ngày mai bạn sẽ:

1. Refine error handling
2. Add comprehensive docstrings
3. Viết unit tests (pytest)
4. Tối ưu performance

**Good luck! 🚀**
