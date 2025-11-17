# 🎓 HƯỚNG DẪN CHI TIẾT - TỪ ĐẦU ĐẾN CUỐI

**Dành cho:** Người mới, chưa hiểu gì về Agent  
**Mục tiêu:** Hiểu 100% cách hoạt động của dự án

---

## 📚 PHẦN 1: HIỂU TỔNG QUAN (Big Picture)

### 🎯 Dự án làm gì?

**Mục tiêu:** Giám sát bảo mật các máy chủ (Ubuntu/Windows) theo chuẩn CIS Benchmark

**Ví dụ thực tế:**
```
Bạn có 10 máy Ubuntu server
├── Server 1: web-server-01
├── Server 2: db-server-01
├── Server 3: app-server-01
└── ...

❓ Làm sao biết server nào KHÔNG ĐẠT chuẩn bảo mật?
✅ Dùng hệ thống Baseline Monitor!
```

---

### 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────┐
│                   DỰ ÁN CỦA BẠN                      │
└─────────────────────────────────────────────────────┘

       ┌──────────────┐         ┌──────────────┐
       │   Backend    │         │   Frontend   │
       │  (Server)    │         │  (Website)   │
       │              │         │              │
       │ - FastAPI    │◄────────┤ - React      │
       │ - PostgreSQL │         │ - Dashboard  │
       └──────▲───────┘         └──────────────┘
              │
              │ HTTP API
              │
    ┌─────────┴──────────────────────────┐
    │                                    │
┌───▼────┐  ┌────────┐  ┌────────┐  ┌───────┐
│ Agent  │  │ Agent  │  │ Agent  │  │ Agent │
│ Server1│  │ Server2│  │ Server3│  │ ...   │
└────────┘  └────────┘  └────────┘  └───────┘
   Ubuntu     Ubuntu     Ubuntu      Windows
```

**Giải thích:**
1. **Backend** = Máy chủ trung tâm (1 máy)
2. **Frontend** = Website để xem kết quả (1 website)
3. **Agent** = Chương trình chạy trên MỖI máy cần giám sát (10 agent = 10 máy)

---

### ❓ Agent là gì?

**Agent** = Chương trình Python chạy trên máy cần giám sát

**Nhiệm vụ của Agent:**
1. ✅ Đăng ký với Backend (lần đầu chạy)
2. ✅ Gửi heartbeat (báo còn sống) mỗi 60 giây
3. ✅ Quét bảo mật theo CIS rules (mỗi 1 giờ)
4. ✅ Gửi kết quả vi phạm lên Backend

**Ví dụ:**
```
10:00 AM - Agent khởi động
10:00 AM - Đăng ký với Backend (lấy agent_id = 7)
10:01 AM - Gửi heartbeat ❤️
10:02 AM - Gửi heartbeat ❤️
10:03 AM - Gửi heartbeat ❤️
...
11:00 AM - Chạy scan bảo mật (10 CIS rules)
11:01 AM - Gửi kết quả: 7 PASS, 3 FAIL
```

---

## 📂 PHẦN 2: HIỂU CẤU TRÚC THỨ MỤC

### Toàn bộ dự án:

```
/home/bach/baseline-monitor/          ← THƯ MỤC GỐC
│
├── backend/                          ← 1. Backend (Server)
│   ├── app/                          │  Code FastAPI
│   ├── venv/                         │  Python virtual env
│   └── requirements.txt              │  Dependencies
│
├── frontend/                         ← 2. Frontend (Website)
│   ├── src/                          │  React code
│   └── package.json                  │  npm dependencies
│
├── agent/                            ← 3. Agent (Chạy trên các máy)
│   ├── common/                       │  Code dùng chung
│   ├── linux/                        │  Code Linux
│   ├── rules/                        │  CIS rules JSON
│   └── setup.py                      │  Wizard tạo config
│
├── config.yaml                       ← 4. Config agent (AUTO-TẠO)
├── .agent_cache.json                 ← 5. Cache agent_id (AUTO-TẠO)
├── logs/                             ← 6. Log files (AUTO-TẠO)
│
├── docs/                             ← 7. Documents
└── README.md                         ← 8. Tổng quan
```

---

### 🔍 CHI TIẾT TỪNG THƯ MỤC

#### 1️⃣ `backend/` - Backend Server

**Mục đích:** Server trung tâm, lưu trữ dữ liệu

**Bạn cần biết:**
- ✅ Chạy trên máy của bạn: `http://localhost:8000`
- ✅ Có database PostgreSQL
- ✅ Có 34+ API endpoints
- ❌ KHÔNG CẦN sửa gì (đã xong)

**Chạy Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Khi nào cần?** Agent cần Backend để đăng ký và gửi dữ liệu

---

#### 2️⃣ `frontend/` - Website Dashboard

**Mục đích:** Website để xem kết quả

**Bạn cần biết:**
- ✅ React app
- ❌ Chưa làm (TUẦN 3-4)

**Tạm thời:** Dùng Postman hoặc curl để test API

---

#### 3️⃣ `agent/` - Code Agent

**Mục đích:** Chương trình chạy trên các máy cần giám sát

**Cấu trúc chi tiết:**

```
agent/
│
├── common/                           ← Code dùng chung
│   ├── config.py                     │  Đọc config.yaml
│   ├── logger.py                     │  Ghi log
│   ├── http_client.py                │  Gọi API Backend
│   ├── models.py                     │  Data models
│   └── system_info.py                │  Lấy thông tin máy
│
├── linux/                            ← Code Linux
│   └── main.py                       │  Chương trình chính
│
├── rules/                            ← CIS rules
│   └── ubuntu_rules.json             │  10 rules Ubuntu
│
└── setup.py                          ← Wizard tạo config
```

**Giải thích từng file:**

---

##### 📄 `agent/common/config.py`

**Mục đích:** Đọc file `config.yaml`

**Code chính:**
```python
config = AgentConfig()
print(config.backend.api_url)    # http://localhost:8000
print(config.agent.hostname)     # web-server-01
```

**Bạn cần biết:**
- Đọc `config.yaml` → trả về Python object
- Đọc `.agent_cache.json` → lấy `agent_id`

---

##### 📄 `agent/common/logger.py`

**Mục đích:** Ghi log ra file

**Code chính:**
```python
from agent.common.logger import setup_logger

logger = setup_logger()
logger.info("✅ Agent started")
# → Ghi vào logs/agent.log
```

**Bạn cần biết:**
- Log ghi vào `logs/agent.log`
- Tự động rotate khi file > 10MB

---

##### 📄 `agent/common/http_client.py`

**Mục đích:** Gọi API Backend

**Code chính:**
```python
client = BackendAPIClient(
    api_url="http://localhost:8000",
    api_token=""
)

# Đăng ký agent
agent_id = client.register_agent(
    hostname="web-server-01",
    ip_address="192.168.1.100"
)
# → Backend trả về agent_id = 7

# Gửi heartbeat
client.send_heartbeat(agent_id)
# → Backend update last_seen
```

**Bạn cần biết:**
- Tất cả HTTP requests đều qua file này
- Có retry logic (thử lại 3 lần nếu fail)

---

##### 📄 `agent/common/system_info.py`

**Mục đích:** Lấy thông tin máy

**Code chính:**
```python
from agent.common.system_info import get_agent_info

info = get_agent_info()
print(info)
# {
#     'hostname': 'web-server-01',
#     'ip_address': '192.168.1.100',
#     'os': 'Ubuntu 20.04.6 LTS',
#     'mac_address': 'aa:bb:cc:dd:ee:ff',
#     'cpu_count': 4,
#     'ram_gb': 8.0
# }
```

**Bạn cần biết:**
- Tự động detect hostname, IP, OS, MAC
- Dùng `socket`, `uuid`, `psutil` libraries

---

##### 📄 `agent/common/models.py`

**Mục đích:** Định nghĩa data structures

**Code chính:**
```python
from agent.common.models import ViolationReport

violation = ViolationReport(
    agent_id=7,
    rule_id="UBU-01",
    status="FAIL",
    details="SSH root login is enabled"
)
```

**Bạn cần biết:**
- Pydantic models để validate dữ liệu
- Giống như class trong OOP

---

##### 📄 `agent/linux/main.py`

**Mục đích:** Chương trình chính của Agent

**Code chính:**
```python
# Run agent
python3 agent/linux/main.py

# Nó làm gì?
1. Đọc config.yaml
2. Check .agent_cache.json → có agent_id chưa?
3. Nếu CHƯA → đăng ký với Backend
4. Nếu RỒI → dùng agent_id đã lưu
5. Loop: gửi heartbeat mỗi 60s
```

**Flow chi tiết:**
```
START
  ↓
Load config.yaml
  ↓
Check backend health (GET /health)
  ↓
Check .agent_cache.json
  ↓
┌─ Có agent_id? ──┐
│                 │
YES              NO
│                 │
Dùng cached      Collect system_info
agent_id=7       POST /api/v1/agents
│                 ↓
│                Backend UPSERT
│                 ↓
│                Return agent_id=7
│                 ↓
│                Save to .agent_cache.json
│                 │
└─────────────────┘
         ↓
  Main Loop (∞)
    Every 60s:
      - Send heartbeat
    Every 1 hour:
      - Run scan (coming soon)
```

---

##### 📄 `agent/setup.py`

**Mục đích:** Wizard tạo `config.yaml`

**Cách dùng:**
```bash
# Interactive mode (có hỏi đáp)
python3 agent/setup.py

# Non-interactive mode
python3 agent/setup.py --backend-url http://192.168.1.100:8000 --no-interactive
```

**Nó làm gì?**
```
1. Auto-detect hostname, IP, OS, MAC
2. Hỏi Backend URL (http://...)
3. Tạo config.yaml với thông tin máy này
4. Test connection tới Backend
5. Done!
```

**Output:**
```yaml
# config.yaml (auto-generated)
backend:
  api_url: http://localhost:8000
agent:
  hostname: web-server-01
  os_type: ubuntu
scanner:
  scan_interval: 3600
  rules_path: ./agent/rules/ubuntu_rules.json
logging:
  level: INFO
  log_file: ./logs/agent.log
```

---

## 🎬 PHẦN 3: WORKFLOW THỰC TẾ - TỪNG BƯỚC

### Scenario: Cài Agent lên 1 máy Ubuntu mới

**Máy:** `web-server-01` (IP: 192.168.1.100)  
**Backend:** Đang chạy tại `http://192.168.1.50:8000`

---

#### BƯỚC 1: Copy code agent lên máy

```bash
# Trên máy web-server-01
cd /opt
git clone https://github.com/xuanbach152/baseline-monitor.git
cd baseline-monitor
```

**Giải thích:** Copy toàn bộ code về máy

---

#### BƯỚC 2: Chạy setup wizard

```bash
python3 agent/setup.py
```

**Output:**
```
🚀 BASELINE MONITOR - AGENT SETUP WIZARD

📊 STEP 1: Collecting System Information
✅ System information collected:
   • Hostname:        web-server-01
   • IP Address:      192.168.1.100
   • OS:              Ubuntu 20.04.6 LTS
   • MAC Address:     aa:bb:cc:dd:ee:ff

🌐 STEP 2: Backend Server Configuration
 Backend URL: █
```

**Bạn nhập:** `http://192.168.1.50:8000`

```
✅ Backend URL saved

🔍 STEP 3: Scanner Configuration
✅ Auto-detected OS type: ubuntu
   Rules file: ./agent/rules/ubuntu_rules.json
   Scan interval: 3600s

💾 STEP 4: Generating Configuration File
✅ Configuration file created: config.yaml

🔌 STEP 5: Testing Backend Connection
✅ Backend is reachable and healthy!

🎉 SETUP COMPLETE!
```

**Kết quả:**
- ✅ File `config.yaml` được tạo với thông tin máy `web-server-01`

---

#### BƯỚC 3: Xem config vừa tạo

```bash
cat config.yaml
```

**Output:**
```yaml
# Generated by Agent Setup Wizard
# Date: 2025-11-17 10:00:00
# Hostname: web-server-01

backend:
  api_url: http://192.168.1.50:8000
  api_token: ""
  timeout: 30
  retry_attempts: 3

agent:
  hostname: web-server-01
  os_type: ubuntu

scanner:
  scan_interval: 3600
  rules_path: ./agent/rules/ubuntu_rules.json
  command_timeout: 10
  report_pass_results: false

logging:
  level: INFO
  log_file: ./logs/agent.log
  max_bytes: 10485760
  backup_count: 5
  console_output: true
```

**Giải thích:**
- ✅ `hostname: web-server-01` = TÊN MÁY NÀY
- ✅ `api_url: http://192.168.1.50:8000` = Backend server
- ✅ `os_type: ubuntu` = Auto-detect
- ✅ `rules_path: ./agent/rules/ubuntu_rules.json` = CIS rules cho Ubuntu

---

#### BƯỚC 4: Chạy agent lần đầu

```bash
python3 agent/linux/main.py
```

**Output:**
```
============================================================
🚀 LINUX AGENT STARTING...
============================================================

📄 Loading config from: config.yaml
   ✅ Config loaded successfully
   📍 Hostname: web-server-01
   🖥️  OS Type: ubuntu
   🌐 Backend: http://192.168.1.50:8000

🏥 Checking backend health...
   ✅ Backend is healthy

🔐 Agent Registration Flow
------------------------------------------------------------
   ❌ No cached agent_id found
   📝 Registering with backend...
   
   Sending to Backend:
   {
       "hostname": "web-server-01",
       "ip_address": "192.168.1.100",
       "os": "Ubuntu 20.04.6 LTS",
       "mac_address": "aa:bb:cc:dd:ee:ff",
       "version": "1.0.0"
   }
   
   ✅ Registration successful! Agent ID: 7
   💾 Saved agent_id to cache: .agent_cache.json

============================================================
✅ AGENT STARTED SUCCESSFULLY
============================================================
   🆔 Agent ID: 7
   📍 Hostname: web-server-01
   💓 Heartbeat interval: 60 seconds

   Press Ctrl+C to stop...
============================================================

💓 Sending heartbeat... ✅
💓 Sending heartbeat... ✅
💓 Sending heartbeat... ✅
...
```

**Giải thích:**
1. ✅ Đọc `config.yaml`
2. ✅ Check backend (GET /health)
3. ✅ Không tìm thấy `.agent_cache.json` → đăng ký mới
4. ✅ POST /api/v1/agents → Backend trả về `agent_id = 7`
5. ✅ Lưu `{"agent_id": 7}` vào `.agent_cache.json`
6. ✅ Bắt đầu gửi heartbeat mỗi 60s

---

#### BƯỚC 5: Xem cache file

```bash
cat .agent_cache.json
```

**Output:**
```json
{"agent_id": 7}
```

**Giải thích:**
- File này LƯU `agent_id` sau lần đăng ký đầu tiên
- Lần sau chạy agent → KHÔNG cần đăng ký lại, dùng `agent_id = 7`

---

#### BƯỚC 6: Stop agent (Ctrl+C)

```
^C
⚠️  Received shutdown signal...
🛑 Shutting down agent...
   ✅ Agent stopped
```

---

#### BƯỚC 7: Chạy agent lần 2

```bash
python3 agent/linux/main.py
```

**Output:**
```
============================================================
🚀 LINUX AGENT STARTING...
============================================================

📄 Loading config from: config.yaml
   ✅ Config loaded successfully

🏥 Checking backend health...
   ✅ Backend is healthy

🔐 Agent Registration Flow
------------------------------------------------------------
   ✅ Found cached agent_id: 7          ← KHÁC LẦN 1!
   📦 Using cached registration         ← KHÔNG ĐĂNG KÝ LẠI!

============================================================
✅ AGENT STARTED SUCCESSFULLY
============================================================
   🆔 Agent ID: 7
   
💓 Sending heartbeat... ✅
💓 Sending heartbeat... ✅
...
```

**Giải thích:**
- ✅ Đọc `.agent_cache.json` → tìm thấy `agent_id = 7`
- ✅ SKIP đăng ký, dùng ngay `agent_id = 7`
- ✅ Gửi heartbeat như bình thường

---

## 🤔 PHẦN 4: CÂU HỎI THƯỜNG GẶP

### ❓ Tại sao cần `config.yaml`?

**Trả lời:** Mỗi máy có thông tin KHÁC NHAU:
- Máy 1: `web-server-01`, IP `192.168.1.100`
- Máy 2: `db-server-01`, IP `192.168.1.101`
- Máy 3: `app-server-01`, IP `192.168.1.102`

→ Mỗi máy cần 1 file `config.yaml` RIÊNG với hostname riêng

---

### ❓ Tại sao cần `.agent_cache.json`?

**Trả lời:** Để KHÔNG phải đăng ký lại mỗi lần chạy agent

**Nếu không có cache:**
```
Lần 1: Đăng ký → agent_id = 7
Lần 2: Đăng ký → agent_id = 8  ← Duplicate!
Lần 3: Đăng ký → agent_id = 9  ← Duplicate!
```

**Có cache:**
```
Lần 1: Đăng ký → agent_id = 7, lưu vào cache
Lần 2: Dùng cache → agent_id = 7  ← Same!
Lần 3: Dùng cache → agent_id = 7  ← Same!
```

---

### ❓ Tại sao cần `logs/`?

**Trả lời:** Để debug khi có lỗi

**Ví dụ:**
```bash
# Agent đột ngột stop, xem log để biết lý do
tail -f logs/agent.log

# Output:
2025-11-17 10:00:00 | ERROR | Connection error: Backend unreachable
```

---

### ❓ `scripts/` dùng để làm gì?

**Trả lời:** Test scripts (không bắt buộc)

**Ví dụ:**
```bash
# Test auto-registration flow
./scripts/test_auto_registration.sh

# Nó làm gì?
1. Xóa .agent_cache.json
2. Chạy agent 30s
3. Check agent_id đã được lưu chưa
```

---

### ❓ Tôi có cần sửa code trong `agent/common/` không?

**Trả lời:** KHÔNG!

**Lý do:**
- `config.py` - Đọc config (không cần sửa)
- `logger.py` - Ghi log (không cần sửa)
- `http_client.py` - Gọi API (không cần sửa)
- `system_info.py` - Lấy thông tin máy (không cần sửa)

**Bạn chỉ cần:**
1. ✅ Chạy `setup.py` → tạo `config.yaml`
2. ✅ Chạy `main.py` → agent hoạt động

---

## 🎯 PHẦN 5: TỔNG KẾT - LÀM GÌ VỚI GÌ

### 🖥️ Trên máy Backend (1 máy)

```bash
# 1. Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# → Backend chạy tại http://192.168.1.50:8000
```

---

### 🤖 Trên máy cần giám sát (nhiều máy)

**Máy 1:**
```bash
cd /opt/baseline-monitor
python3 agent/setup.py
# → Tạo config.yaml với hostname: web-server-01
python3 agent/linux/main.py
# → Agent chạy, agent_id = 7
```

**Máy 2:**
```bash
cd /opt/baseline-monitor
python3 agent/setup.py
# → Tạo config.yaml với hostname: db-server-01
python3 agent/linux/main.py
# → Agent chạy, agent_id = 8
```

**Máy 3:**
```bash
cd /opt/baseline-monitor
python3 agent/setup.py
# → Tạo config.yaml với hostname: app-server-01
python3 agent/linux/main.py
# → Agent chạy, agent_id = 9
```

---

## 🎬 PHẦN 6: DEMO THỰC TẾ - THEO TÔI LÀM

### Scenario: Setup agent trên máy của bạn

**Giả sử:**
- Backend đang chạy: `http://localhost:8000`
- Máy bạn: `bach-HP-ZBook-...`

---

#### ✅ BƯỚC 1: Check backend

```bash
curl http://localhost:8000/health
```

**Output mong đợi:**
```json
{"status":"healthy"}
```

**Nếu lỗi:** Start backend trước:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

---

#### ✅ BƯỚC 2: Chạy setup wizard

```bash
cd /home/bach/baseline-monitor
python3 agent/setup.py --backend-url http://localhost:8000 --no-interactive
```

**Output:**
```
🚀 BASELINE MONITOR - AGENT SETUP WIZARD

📊 STEP 1: Collecting System Information
✅ System information collected:
   • Hostname:        bach-HP-ZBook-Power-16-inch-G11-A-Mobile-Workstation-PC
   • IP Address:      192.168.1.174
   • OS:              Ubuntu 24.04.3 LTS

💾 STEP 4: Generating Configuration File
✅ Configuration file created: config.yaml

🔌 STEP 5: Testing Backend Connection
✅ Backend is reachable and healthy!

🎉 SETUP COMPLETE!
```

---

#### ✅ BƯỚC 3: Xem config

```bash
cat config.yaml
```

**Check:**
- ✅ `hostname` đúng tên máy bạn
- ✅ `api_url: http://localhost:8000`
- ✅ `os_type: ubuntu`

---

#### ✅ BƯỚC 4: Chạy agent

```bash
python3 agent/linux/main.py
```

**Quan sát:**
```
🔐 Agent Registration Flow
------------------------------------------------------------
   ❌ No cached agent_id found          ← Lần đầu
   📝 Registering with backend...
   ✅ Registration successful! Agent ID: 7
   💾 Saved agent_id to cache
```

---

#### ✅ BƯỚC 5: Check backend

```bash
# Terminal khác
curl http://localhost:8000/api/v1/agents
```

**Output:**
```json
[
  {
    "id": 7,
    "hostname": "bach-HP-ZBook-Power-16-inch-G11-A-Mobile-Workstation-PC",
    "ip_address": "192.168.1.174",
    "is_online": true,
    "last_checkin": "2025-11-17T10:05:00Z"
  }
]
```

**✅ THÀNH CÔNG! Agent đã đăng ký với backend!**

---

#### ✅ BƯỚC 6: Stop và chạy lại

```bash
# Stop agent (Ctrl+C)
^C

# Chạy lại
python3 agent/linux/main.py
```

**Quan sát:**
```
🔐 Agent Registration Flow
------------------------------------------------------------
   ✅ Found cached agent_id: 7          ← Lần 2: dùng cache
   📦 Using cached registration
```

**✅ HOÀN HẢO! Agent dùng cache, không đăng ký lại!**

---

## 📚 PHẦN 7: ĐỌC CODE NHƯ THẾ NÀO?

### Thứ tự đọc (từ dễ đến khó):

1. **`agent/setup.py`** (350 lines)
   - Dễ hiểu nhất
   - Tạo config.yaml
   - Đọc để hiểu flow setup

2. **`agent/common/system_info.py`** (100 lines)
   - Lấy hostname, IP, OS
   - Pure Python, dễ hiểu

3. **`agent/common/logger.py`** (80 lines)
   - Setup logger
   - Đơn giản

4. **`agent/common/config.py`** (150 lines)
   - Đọc YAML file
   - Cache mechanism
   - Hơi phức tạp

5. **`agent/linux/main.py`** (267 lines)
   - Main agent logic
   - Registration flow
   - Heartbeat loop
   - Phức tạp nhất

6. **`agent/common/http_client.py`** (350 lines)
   - HTTP requests
   - Retry logic
   - Nâng cao

7. **`agent/common/models.py`** (150 lines)
   - Pydantic models
   - Data structures
   - Cần hiểu Pydantic

---

### Tips đọc code:

1. **Đọc từ trên xuống:**
   - Imports → Class → Methods → Main

2. **Đọc docstrings:**
   ```python
   def register_agent(self, hostname: str) -> int:
       """
       Đăng ký agent với backend.
       
       Args:
           hostname: Tên máy
           
       Returns:
           agent_id nếu thành công
       """
   ```

3. **Chạy từng function riêng:**
   ```python
   # Test system_info
   python3 -c "from agent.common.system_info import get_agent_info; print(get_agent_info())"
   ```

4. **Đọc logs:**
   ```bash
   tail -f logs/agent.log
   ```

---

## 🎯 KẾT LUẬN

### Bạn CẦN HIỂU:

✅ **Backend** = Server trung tâm (đã xong)  
✅ **Agent** = Chương trình chạy trên mỗi máy  
✅ **config.yaml** = Config riêng cho mỗi máy (auto-tạo bởi setup.py)  
✅ **.agent_cache.json** = Cache agent_id (auto-tạo sau đăng ký)  
✅ **logs/** = Log files (auto-tạo)  

### Bạn KHÔNG CẦN SỬA:

❌ `agent/common/*.py` - Code modules (đã xong)  
❌ `agent/linux/main.py` - Agent logic (đã xong)  
❌ Backend code - API (đã xong)  

### Bạn CHỈ CẦN LÀM:

1. ✅ Start backend:
   ```bash
   cd backend && uvicorn app.main:app --reload
   ```

2. ✅ Trên mỗi máy agent:
   ```bash
   python3 agent/setup.py
   python3 agent/linux/main.py
   ```

3. ✅ DONE! Agent hoạt động!

---

### TIẾP THEO: TUẦN 1 - Ubuntu Scanner

**Làm gì?**
- Implement scan logic trong `agent/linux/scanner.py`
- Load 10 CIS rules từ `agent/rules/ubuntu_rules.json`
- Execute shell commands
- Report violations lên backend

**Nhưng TẠM THỜI:**
- Agent core đã xong ✅
- Auto-registration đã xong ✅
- Heartbeat đã xong ✅

---

**🎉 Giờ bạn đã HIỂU 100% cấu trúc dự án!**

**Có thắc mắc gì, cứ hỏi từng bước nhỏ nhỏ!** 😊
