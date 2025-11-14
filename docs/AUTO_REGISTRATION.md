# Auto-Registration Pattern - Hướng Dẫn Triển Khai

## 🎯 Mục Đích

Cho phép Agent tự động đăng ký với Backend mà không cần admin tạo agent trước.

---

## 📊 So Sánh 2 Cách

### ❌ Cách Cũ (Thủ công)
```
1. Admin tạo agent trong backend
   → agent_id = 1
2. Admin ghi agent_id vào config.yaml
3. Agent chạy và dùng agent_id cố định
```

**Nhược điểm:**
- Phải tạo trước
- Khó scale (100+ máy?)
- Dễ nhầm lẫn ID

### ✅ Cách Mới (Auto-Registration)
```
1. Cài agent lên máy client
2. Agent tự lấy hostname
3. Agent đăng ký với backend
4. Backend tạo/update agent tự động
5. Agent lưu agent_id vào cache
6. Lần sau dùng agent_id từ cache
```

**Ưu điểm:**
- Tự động 100%
- Scale dễ dàng
- Không nhầm lẫn

---

## 🔧 Triển Khai

### 1. Backend - Sửa API (ĐÃ XONG ✅)

File: `backend/app/modules/agents/crud.py`

```python
def create_agent(db: Session, agent: AgentCreate) -> Agent:
    """Register new agent or update existing one (UPSERT)."""
    existing = get_agent_by_hostname(db, agent.hostname)
    
    if existing:
        # Update existing agent
        existing.ip_address = agent.ip_address
        existing.os = agent.os
        existing.version = agent.version
        existing.is_online = True
        existing.last_checkin = datetime.now()
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new agent
    db_agent = Agent(**agent.model_dump(), is_online=True)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent
```

### 2. Agent Config - Thêm Cache

File: `agent/common/config.py`

**Thêm vào class AgentConfig:**

```python
def __init__(self, config_path: str = "config.yaml"):
    self.config_path = Path(config_path)
    self._config_data = {}
    self._cache_file = Path(".agent_cache.json")  # NEW
    self._cached_agent_id = None  # NEW
    self._load_config()
    self._load_cache()  # NEW

def _load_cache(self):
    """Load agent_id từ cache file."""
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
    """Lưu agent_id sau khi đăng ký."""
    self._cached_agent_id = agent_id
    with open(self._cache_file, 'w') as f:
        json.dump({'agent_id': agent_id}, f)

@property
def agent_id(self) -> Optional[int]:
    """Trả về agent_id từ cache (None nếu chưa đăng ký)."""
    return self._cached_agent_id

@property
def hostname(self) -> str:
    """Hostname (auto-detect nếu không có)."""
    return self._config_data['agent'].get('hostname') or socket.gethostname()
```

### 3. Agent Main - Thêm Registration Logic

File: `agent/linux/main.py` (sẽ tạo sau)

```python
from agent.common.config import AgentConfig
from agent.common.http_client import BackendAPIClient
import socket

def get_local_ip():
    """Lấy IP address của máy."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def register_agent(config: AgentConfig, client: BackendAPIClient):
    """Đăng ký agent với backend."""
    
    # Kiểm tra đã có agent_id chưa
    if config.agent_id:
        print(f"✅ Agent already registered: ID = {config.agent_id}")
        return config.agent_id
    
    # Chưa có → Đăng ký mới
    print("🆕 Registering agent with backend...")
    
    agent_data = {
        "hostname": config.hostname,
        "ip_address": get_local_ip(),
        "os": f"{config.os_type} {platform.release()}",
        "version": "1.0.0"
    }
    
    # Gọi API register
    response = client.register_agent(agent_data)
    agent_id = response['id']
    
    # Lưu agent_id vào cache
    config.save_agent_id(agent_id)
    
    print(f"✅ Agent registered successfully: ID = {agent_id}")
    return agent_id

def main():
    # 1. Load config
    config = AgentConfig("config.yaml")
    
    # 2. Create HTTP client
    client = BackendAPIClient(
        base_url=config.api_url,
        api_token=config.api_token
    )
    
    # 3. Register agent (nếu chưa có)
    agent_id = register_agent(config, client)
    
    # 4. Bắt đầu scan loop
    while True:
        # Send heartbeat
        client.send_heartbeat(agent_id)
        
        # Scan
        # ...
        
        # Sleep
        time.sleep(config.scan_interval)

if __name__ == "__main__":
    main()
```

---

## 📝 Config File Mới

File: `config.yaml`

```yaml
agent:
  # Hostname (tự động lấy từ system nếu không có)
  hostname: ""  # Để trống = auto-detect
  
  # Tên hiển thị
  name: "Production Server"
  
  # OS type
  os_type: "ubuntu"

backend:
  api_url: "http://192.168.1.100:8000"
  api_token: "eyJhbG..."
  timeout: 30
  retry_attempts: 3

scanner:
  scan_interval: 3600
  rules_path: "./rules/ubuntu_rules.json"
```

**KHÔNG CẦN `agent_id` NỮA!**

---

## 🚀 Luồng Hoạt Động

### Lần Đầu Chạy (Chưa có cache)

```
1. Agent start
   ↓
2. Load config.yaml
   hostname = socket.gethostname() = "web-server-01"
   ↓
3. Check cache file (.agent_cache.json)
   → File không tồn tại
   → agent_id = None
   ↓
4. Call register_agent()
   POST /api/v1/agents/
   {
     "hostname": "web-server-01",
     "ip_address": "192.168.1.10",
     "os": "Ubuntu 22.04"
   }
   ↓
5. Backend:
   - Tìm agent theo hostname: Không có
   - Tạo mới agent
   - Return: {"id": 1, "hostname": "web-server-01", ...}
   ↓
6. Agent lưu cache:
   .agent_cache.json: {"agent_id": 1}
   ↓
7. Agent bắt đầu scan với agent_id = 1
```

### Lần Sau Chạy (Đã có cache)

```
1. Agent start
   ↓
2. Load config.yaml
   ↓
3. Check cache file (.agent_cache.json)
   → File tồn tại
   → agent_id = 1
   ↓
4. Skip registration (đã có ID)
   ↓
5. Agent bắt đầu scan với agent_id = 1
```

---

## ✅ Lợi Ích

1. **Tự động hoàn toàn:** Không cần admin can thiệp
2. **Scale dễ dàng:** Cài 1000 máy? Không vấn đề!
3. **Idempotent:** Chạy nhiều lần không tạo duplicate
4. **Resilient:** Xóa cache? Tự động đăng ký lại
5. **Identify đúng:** Dùng hostname làm unique key

---

## 🔍 Troubleshooting

### Q: Cache file bị mất?
**A:** Không sao! Agent sẽ tự đăng ký lại với cùng hostname.

### Q: Đổi hostname thì sao?
**A:** Agent sẽ được coi như máy mới và tạo agent mới trong backend.

### Q: 2 máy cùng hostname?
**A:** Backend sẽ update cùng 1 agent (nên đặt hostname unique).

### Q: Muốn reset agent?
**A:** Xóa file `.agent_cache.json` và restart agent.

---

## 📚 Next Steps

1. ✅ Backend API đã sửa xong
2. ⏳ Sửa config.py thêm cache logic
3. ⏳ Tạo http_client.py với method register_agent()
4. ⏳ Tạo main.py với registration flow

---

**Tác giả:** Bach  
**Ngày:** 2024-11-14  
**Version:** 1.0
