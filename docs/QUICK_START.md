# QUICK START - Cài Đặt Agent Trong 2 Phút

## 🎯 3 Cách Cài Đặt Agent

### ✅ CÁCH 1: Setup Wizard (KHUYẾN NGHỊ - DỄ NHẤT)

**Dùng khi:** Cài đặt trên bất kỳ máy nào (local hoặc production)

**Ưu điểm:**
- ✅ Tự động detect hostname, OS, IP, MAC
- ✅ Tự động generate `config.yaml` phù hợp với máy
- ✅ Test kết nối backend
- ✅ Không cần chỉnh config thủ công

**Cách dùng:**

```bash
# Interactive mode (có hỏi đáp)
python3 agent/setup.py

# Non-interactive mode (dùng cho automation/scripts)
python3 agent/setup.py \
  --backend-url http://192.168.1.100:8000 \
  --no-interactive
```

**Output:**
```
🚀 BASELINE MONITOR - AGENT SETUP WIZARD

📊 STEP 1: Collecting System Information
✅ System information collected:
   • Hostname:        web-server-01
   • IP Address:      192.168.1.174
   • OS:              Ubuntu 24.04.3 LTS
   • MAC Address:     aa:bb:cc:dd:ee:ff

🌐 STEP 2: Backend Server Configuration
 Backend URL: http://192.168.1.100:8000

🔍 STEP 3: Scanner Configuration
✅ Auto-detected OS type: ubuntu
   Rules file: ./agent/rules/ubuntu_rules.json

💾 STEP 4: Generating Configuration File
✅ Configuration file created: config.yaml

🔌 STEP 5: Testing Backend Connection
✅ Backend is reachable and healthy!

🎉 SETUP COMPLETE!
✅ Agent is ready to run!
```

**File được tạo:**
- `config.yaml` — tự động generate với thông tin máy này
- Backup: `config.yaml.backup` (nếu file cũ tồn tại)

---

### ✅ CÁCH 2: Bootstrap Script (Dùng Cho SSH/Ansible)

**Dùng khi:** Deploy lên nhiều máy qua SSH hoặc Ansible

**Ưu điểm:**
- ✅ Bash script đơn giản
- ✅ Dễ dàng SSH và chạy
- ✅ Hỗ trợ flags đầy đủ

**Cách dùng:**

```bash
# Local
./scripts/bootstrap_agent.sh \
  --api-url http://backend:8000 \
  --os-type ubuntu

# Remote qua SSH
ssh user@server1 "cd /opt/agent && \
  ./scripts/bootstrap_agent.sh \
  --api-url http://backend:8000 \
  --os-type ubuntu"
```

---

### ✅ CÁCH 3: Thủ Công (Development/Testing)

**Dùng khi:** Dev/test trên máy local, muốn control hoàn toàn

**Cách dùng:**

```bash
# Copy template
cp agent/config.example.yaml config.yaml

# Edit file
vim config.yaml
# Sửa: api_url, hostname, os_type...
```

---

## 🚀 SO SÁNH 3 CÁCH

| Feature | Setup Wizard | Bootstrap Script | Thủ công |
|---------|--------------|------------------|----------|
| Auto-detect system info | ✅ | ❌ | ❌ |
| Interactive wizard | ✅ | ❌ | ❌ |
| Test backend connection | ✅ | ❌ | ❌ |
| Non-interactive mode | ✅ | ✅ | ❌ |
| SSH-friendly | ✅ | ✅ | ⚠️ |
| Ansible-friendly | ✅ | ✅ | ⚠️ |
| Control hoàn toàn | ⚠️ | ⚠️ | ✅ |

**Khuyến nghị:**
- 🥇 **Setup Wizard** — dùng cho 90% trường hợp
- 🥈 **Bootstrap Script** — dùng khi cần bash script thuần
- 🥉 **Thủ công** — chỉ khi dev/debug

---

## 📋 WORKFLOW THỰC TẾ

### Scenario 1: Cài Agent Trên 1 Máy Production

```bash
# 1. Copy agent code lên server
scp -r agent/ user@server:/opt/baseline-monitor/

# 2. SSH vào server
ssh user@server

# 3. Run setup wizard
cd /opt/baseline-monitor
python3 agent/setup.py

# Wizard sẽ hỏi:
# - Backend URL: http://backend.company.com:8000
# - API Token: (nhấn Enter nếu không cần)
# - Scan interval: 3600

# 4. Start agent
python3 agent/linux/main.py
```

---

### Scenario 2: Cài Agent Trên 50 Máy (Automation)

**Option A: SSH Loop**
```bash
#!/bin/bash
SERVERS="server1 server2 server3 ... server50"
BACKEND="http://backend.company.com:8000"

for server in $SERVERS; do
  echo "Setting up $server..."
  
  ssh user@$server "cd /opt/baseline-monitor && \
    python3 agent/setup.py \
      --backend-url $BACKEND \
      --no-interactive && \
    systemctl start baseline-agent"
done
```

**Option B: Ansible Playbook**
```yaml
---
- name: Setup Baseline Monitor Agent
  hosts: all
  vars:
    backend_url: "http://backend.company.com:8000"
  tasks:
    - name: Copy agent code
      copy:
        src: agent/
        dest: /opt/baseline-monitor/agent/
    
    - name: Run setup wizard
      command: >
        python3 /opt/baseline-monitor/agent/setup.py
        --backend-url {{ backend_url }}
        --no-interactive
    
    - name: Start agent service
      systemd:
        name: baseline-agent
        state: started
        enabled: yes
```

---

### Scenario 3: Cloud-Init (AWS/GCP/Azure)

```yaml
#cloud-config
runcmd:
  - cd /opt/baseline-monitor
  - python3 agent/setup.py --backend-url http://backend:8000 --no-interactive
  - systemctl start baseline-agent
```

---

## 🔍 KIỂM TRA SETUP

### 1. Xem Config Đã Tạo
```bash
cat config.yaml
```

**Kết quả mong đợi:**
```yaml
backend:
  api_url: http://backend:8000
agent:
  hostname: web-server-01      # ← Auto-detect
  os_type: ubuntu               # ← Auto-detect
scanner:
  scan_interval: 3600
  rules_path: ./agent/rules/ubuntu_rules.json
logging:
  level: INFO
  log_file: ./logs/agent.log
```

### 2. Test Backend Connection
```bash
curl http://backend:8000/health
```

### 3. Start Agent
```bash
python3 agent/linux/main.py
```

**Output mong đợi:**
```
🚀 LINUX AGENT STARTING...
✅ Config loaded successfully
✅ Backend is healthy
✅ Registration successful! Agent ID: 7
✅ AGENT STARTED SUCCESSFULLY
```

### 4. Check Agent In Backend
```bash
curl http://backend:8000/api/v1/agents
```

---

## 🆚 SO SÁNH VỚI CÁCH CŨ

### ❌ Cách Cũ (Phức tạp)
```bash
# 1. Copy template
cp agent/config.example.yaml config.yaml

# 2. Get hostname manually
hostname

# 3. Get IP manually
ip addr | grep inet

# 4. Get OS manually
cat /etc/os-release

# 5. Edit config manually
vim config.yaml
# Sửa 10 dòng khác nhau...

# 6. Test manually
curl http://backend:8000/health

# 7. Run
python3 agent/linux/main.py
```

### ✅ Cách Mới (Đơn giản)
```bash
# 1 lệnh duy nhất
python3 agent/setup.py

# Wizard làm tất cả:
# - Auto-detect hostname ✅
# - Auto-detect IP ✅
# - Auto-detect OS ✅
# - Generate config ✅
# - Test backend ✅
```

**Tiết kiệm:** ~5 phút/máy → Với 50 máy = tiết kiệm 4 giờ!

---

## 🎓 CHI TIẾT SETUP WIZARD

### Interactive Mode (Có Hỏi Đáp)

```bash
python3 agent/setup.py
```

**Wizard sẽ hỏi:**
1. Backend URL → Bạn nhập: `http://192.168.1.100:8000`
2. API Token (optional) → Nhấn Enter để skip
3. Scan interval → Nhập `3600` hoặc Enter để dùng mặc định

### Non-Interactive Mode (Automation)

```bash
# Dùng flags
python3 agent/setup.py \
  --backend-url http://backend:8000 \
  --api-token "eyJhbG..." \
  --no-interactive

# Hoặc dùng env vars
export AGENT_BACKEND_URL="http://backend:8000"
export AGENT_API_TOKEN="eyJhbG..."
export AGENT_SCAN_INTERVAL="3600"

python3 agent/setup.py --no-interactive
```

### Flags Hỗ Trợ

```
--backend-url URL        Backend server URL
--api-token TOKEN        API authentication token
--no-interactive         Skip all prompts (use env vars/defaults)
-h, --help              Show help
```

---

## 🐛 TROUBLESHOOTING

### Q: Setup wizard báo "Backend is unreachable"?
**A:** Không sao! Wizard vẫn tạo config. Bạn start backend sau rồi run agent.

### Q: Muốn đổi backend URL sau khi setup?
**A:** Chạy lại setup wizard hoặc edit `config.yaml` thủ công.

### Q: File config.yaml đã tồn tại?
**A:** Wizard sẽ hỏi có overwrite không. Nếu có, file cũ được backup thành `config.yaml.backup`.

### Q: Làm sao xóa config và setup lại từ đầu?
```bash
rm config.yaml .agent_cache.json
python3 agent/setup.py
```

---

## 📊 METRICS

**Setup Time Comparison:**

| Method | Time per Machine | Time for 50 Machines |
|--------|------------------|----------------------|
| Thủ công | ~5 phút | ~4 giờ |
| Bootstrap | ~2 phút | ~1.5 giờ |
| **Setup Wizard** | **~1 phút** | **~1 giờ** |

**Error Rate:**

| Method | Human Error Risk |
|--------|------------------|
| Thủ công | ⚠️ High (typos, wrong OS, wrong IP) |
| Bootstrap | ⚠️ Medium (wrong flags) |
| **Setup Wizard** | ✅ **Low (auto-detect)** |

---

## ✅ CHECKLIST SAU KHI SETUP

- [ ] File `config.yaml` đã được tạo
- [ ] Hostname trong config khớp với `hostname` command
- [ ] Backend URL đúng
- [ ] Test connection thành công (hoặc backend chưa chạy - OK)
- [ ] Agent start được: `python3 agent/linux/main.py`
- [ ] Agent đăng ký thành công (có agent_id)
- [ ] File `.agent_cache.json` được tạo
- [ ] Heartbeat gửi thành công mỗi 60s

---

**🎉 Giờ bạn có thể cài agent lên bất kỳ máy nào trong 1 phút!**

## 🔜 Next Steps

Sau khi agent đã chạy:
1. Xem logs: `tail -f logs/agent.log`
2. Check trong backend: `curl http://backend:8000/api/v1/agents`
3. Chờ scanner được implement (coming soon...)
