# Agent System Information Collection

## 📋 Thông Tin Agent Thu Thập

### **1. Thông Tin Bắt Buộc**

| Field | Mô Tả | Ví Dụ | Cách Lấy |
|-------|-------|-------|----------|
| `hostname` | Tên máy | `web-server-01` | `socket.gethostname()` |
| `ip_address` | IP local | `192.168.1.10` | Socket connect trick |
| `os` | Hệ điều hành | `Ubuntu 22.04.3 LTS` | `/etc/os-release` hoặc `platform` |
| `version` | Agent version | `1.0.0` | Hardcode hoặc từ config |

### **2. Thông Tin Optional**

| Field | Mô Tả | Dùng Để |
|-------|-------|---------|
| `mac_address` | MAC address | Identify máy unique |
| `public_ip` | IP public | Biết IP ra internet |
| `cpu` | CPU info | Monitoring |
| `memory` | RAM info | Monitoring |
| `disk` | Disk info | Monitoring |

---

## 🔧 Module `system_info.py`

### **Cài Đặt Dependencies**

```bash
# Trong venv
pip install psutil

# Hoặc thêm vào requirements.txt
psutil==5.9.8
```

### **Sử Dụng**

```python
from agent.common.system_info import get_agent_info

# Thu thập thông tin basic
info = get_agent_info()
print(info)
# {
#     'hostname': 'web-server-01',
#     'ip_address': '192.168.1.10',
#     'os': 'Ubuntu 22.04.3 LTS',
#     'mac_address': 'aa:bb:cc:dd:ee:ff',
#     'version': '1.0.0'
# }

# Thu thập thêm system stats (CPU, RAM, Disk)
info = get_agent_info(include_system_stats=True)
print(info)
# {
#     ...
#     'cpu': {'physical_cores': 4, 'logical_cores': 8, ...},
#     'memory': {'total_gb': 16.0, 'available_gb': 8.5, ...},
#     'disk': {'total_gb': 500.0, 'used_gb': 250.0, ...}
# }
```

---

## 📝 Luồng Đăng Ký Agent

### **Code Example**

```python
# File: agent/linux/main.py

from agent.common.system_info import get_agent_info
from agent.common.http_client import BackendAPIClient

def register_agent(client: BackendAPIClient):
    """Đăng ký agent với backend."""
    
    # 1. Thu thập thông tin hệ thống
    print("📊 Collecting system information...")
    agent_data = get_agent_info()
    
    print(f"   Hostname:   {agent_data['hostname']}")
    print(f"   IP:         {agent_data['ip_address']}")
    print(f"   OS:         {agent_data['os']}")
    print(f"   MAC:        {agent_data['mac_address']}")
    
    # 2. Gửi lên backend
    print("📤 Registering with backend...")
    response = client.register_agent(agent_data)
    
    # 3. Nhận agent_id
    agent_id = response['id']
    print(f"✅ Agent registered: ID = {agent_id}")
    
    return agent_id
```

---

## 🎯 Data Flow

```
┌─────────────────────────────────────┐
│  Agent Machine (Client)             │
│                                     │
│  1. system_info.get_agent_info()   │
│     ↓                               │
│     {                               │
│       hostname: "web-server-01"    │
│       ip_address: "192.168.1.10"   │
│       os: "Ubuntu 22.04.3 LTS"     │
│       mac_address: "aa:bb:cc:.."   │
│       version: "1.0.0"             │
│     }                               │
│     ↓                               │
│  2. http_client.register_agent()   │
│     ↓                               │
└─────────┬───────────────────────────┘
          │
          │ HTTP POST /api/v1/agents/
          │
          ↓
┌─────────────────────────────────────┐
│  Backend Server                     │
│                                     │
│  1. Nhận data từ agent             │
│     ↓                               │
│  2. Check hostname đã có chưa?     │
│     ├─ Có: Update thông tin        │
│     └─ Chưa: Tạo mới               │
│     ↓                               │
│  3. Lưu vào database               │
│     INSERT/UPDATE agents           │
│     ↓                               │
│  4. Trả về agent_id                │
│     Response: {"id": 1, ...}       │
└─────────┬───────────────────────────┘
          │
          │ HTTP Response
          │
          ↓
┌─────────────────────────────────────┐
│  Agent Machine (Client)             │
│                                     │
│  1. Nhận agent_id = 1              │
│     ↓                               │
│  2. Lưu vào cache                  │
│     .agent_cache.json              │
│     {"agent_id": 1}                │
│     ↓                               │
│  3. Sử dụng agent_id cho scan     │
└─────────────────────────────────────┘
```

---

## 🧪 Testing

### **Test Module Riêng**

```bash
# Test system_info module
cd /home/bach/baseline-monitor
python -m agent.common.system_info

# Output:
# ============================================================
# 🖥️  SYSTEM INFORMATION
# ============================================================
# 
# 📋 Basic Info:
#    Hostname:     ubuntu-desktop
#    Local IP:     192.168.1.10
#    OS:           Ubuntu 22.04.3 LTS
#    MAC Address:  aa:bb:cc:dd:ee:ff
# 
# 🌐 Network:
#    Public IP:    42.118.234.123
# 
# 💻 CPU:
#    Physical Cores: 4
#    Logical Cores:  8
#    Usage:          25.5%
#    Frequency:      2400 MHz
# 
# 💾 Memory:
#    Total:      16.0 GB
#    Available:  8.5 GB
#    Used:       46.9%
# 
# 💿 Disk:
#    Total:  500.0 GB
#    Used:   250.0 GB (50.0%)
#    Free:   250.0 GB
```

### **Test Integration với Backend**

```python
# File: test_registration.py

from agent.common.system_info import get_agent_info
from agent.common.http_client import BackendAPIClient

# 1. Thu thập info
info = get_agent_info()
print(f"Agent Info: {info}")

# 2. Gửi lên backend (giả sử backend đang chạy)
client = BackendAPIClient(
    base_url="http://localhost:8000",
    api_token="your-token"
)

response = client.register_agent(info)
print(f"Backend Response: {response}")
# → {'id': 1, 'hostname': 'web-server-01', 'is_online': True, ...}
```

---

## ⚠️ Lưu Ý

### **1. Permissions**

Một số thông tin cần quyền đặc biệt:
- **Disk usage:** Cần quyền đọc `/`
- **Network stats:** Có thể cần root trên một số OS
- **System info:** Thường OK với user bình thường

### **2. Performance**

- `get_cpu_info()`: Mất 1s (do `cpu_percent(interval=1)`)
- `get_public_ip()`: Mất 1-3s (do gọi API external)
- Các hàm khác: < 0.1s

**Khuyến nghị:**
- Chỉ gọi `get_agent_info()` 1 lần lúc khởi động
- Không gọi trong loop scan

### **3. Error Handling**

Tất cả functions đã có try-except:
- Lỗi → Trả về giá trị mặc định (empty dict, "127.0.0.1", etc.)
- Agent vẫn chạy được dù không lấy được một số thông tin

---

## 📚 References

- **psutil docs:** https://psutil.readthedocs.io/
- **platform module:** https://docs.python.org/3/library/platform.html
- **socket module:** https://docs.python.org/3/library/socket.html

---

**Tác giả:** Bach  
**Ngày:** 2024-11-14  
**Version:** 1.0
