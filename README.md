# 🛡️ Baseline Monitor

**CIS Benchmark Compliance Monitoring System** for Windows 10 and Ubuntu 20.04.

Auto-registration architecture - agents tự động đăng ký với backend khi chạy lần đầu.

---

## 🚀 Quick Start

### 1️⃣ Setup Backend (One-time)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2️⃣ Setup Agent (On Each Machine)
```bash
# Auto-generate config.yaml
python3 agent/setup.py --backend-url http://backend:8000 --no-interactive

# Start agent
python3 agent/linux/main.py
```

**✅ Done!** Agent tự động:
- Collect system info (hostname, IP, OS, MAC)
- Register với backend (UPSERT by hostname)
- Save agent_id vào cache
- Gửi heartbeat mỗi 60s

---

## 📁 Structure

```
baseline-monitor/
├── agent/              # 🤖 Agent (runs on client machines)
│   ├── common/         # Shared modules (config, logger, http_client)
│   ├── linux/          # Linux agent (main.py)
│   ├── rules/          # CIS Benchmark rules (JSON)
│   └── setup.py        # Setup wizard (auto-generate config)
├── backend/            # 🔧 FastAPI + PostgreSQL (34+ endpoints)
├── frontend/           # 🖥️ React dashboard
├── docs/               # 📚 Documentation
│   ├── QUICK_START.md             # 3 ways to setup agent
│   ├── AUTO_REGISTRATION_DETAIL.md # Technical deep-dive
│   ├── LUONG_AGENT_CHI_TIET.md    # Vietnamese guide
│   └── PROJECT_STRUCTURE.md       # File/folder explained
└── scripts/            # 🛠️ Test scripts
```

---

## 🎯 Features

### ✅ Completed
- **Backend:** 34+ REST API endpoints, PostgreSQL, JWT auth, Alembic migrations
- **Agent Core:** Auto-registration, heartbeat, cache mechanism, system info detection
- **Setup Wizard:** Auto-generate machine-specific config.yaml
- **Documentation:** English + Vietnamese guides

### 🚧 In Progress
- **Ubuntu Scanner:** CIS Benchmark rule executor (TUẦN 1)
- **Windows Agent:** PowerShell-based agent (TUẦN 2)
- **Frontend Dashboard:** React UI with real-time updates (TUẦN 3-4)

---

## 📖 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - 3 ways to setup agent
- **[Auto-Registration Detail](docs/AUTO_REGISTRATION_DETAIL.md)** - Technical deep-dive
- **[Luồng Agent Chi Tiết](docs/LUONG_AGENT_CHI_TIET.md)** - Vietnamese explanation
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - File/folder guide

---

## 🏗️ Architecture

### Auto-Registration Flow

```
┌─────────────┐                  ┌─────────────┐
│   Agent     │                  │   Backend   │
│ (client)    │                  │  (server)   │
└──────┬──────┘                  └──────┬──────┘
       │                                │
       │ 1. Load config.yaml            │
       │────────────────────>           │
       │                                │
       │ 2. Check .agent_cache.json     │
       │    → NOT FOUND                 │
       │                                │
       │ 3. Collect system_info         │
       │    (hostname, IP, OS, MAC)     │
       │                                │
       │ 4. POST /api/v1/agents         │
       │    {hostname, ip, os, ...}     │
       │───────────────────────────────>│
       │                                │
       │                    5. UPSERT   │
       │                    (by hostname)
       │                                │
       │ 6. Response: {agent_id: 7}    │
       │<───────────────────────────────│
       │                                │
       │ 7. Save to .agent_cache.json   │
       │    {"agent_id": 7}             │
       │                                │
       │ 8. Start heartbeat loop        │
       │    (every 60s)                 │
       │───────────────────────────────>│
       │<───────────────────────────────│
```

---

## 🧪 Testing

```bash
# Test auto-registration flow
./scripts/test_auto_registration.sh

# Run backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload

# Run agent (in another terminal)
python3 agent/linux/main.py
```

---

## 🛠️ Technology Stack

- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT
- **Agent:** Python 3, PyYAML, psutil, requests
- **Frontend:** React, Vite, TailwindCSS (planned)
- **Infra:** Docker Compose, systemd

---

## 📅 Timeline

- **✅ TUẦN 0:** Backend foundation (34+ endpoints, database, migrations)
- **✅ Day 1:** Agent core + auto-registration
- **🚧 TUẦN 1:** Ubuntu Scanner (10 CIS rules)
- **⏳ TUẦN 2:** Windows Agent
- **⏳ TUẦN 3-4:** Frontend Dashboard
- **⏳ TUẦN 5-6:** Integration Testing
- **⏳ TUẦN 7-8:** Documentation & Thesis

---

## 📝 License

MIT License - use freely for your thesis/project.

---

**Made with ❤️ for CIS Benchmark compliance monitoring**
