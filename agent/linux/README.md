# Linux Agent - Baseline Monitor

Ubuntu/Linux CIS Benchmark Compliance Agent với auto-registration và real-time scanning.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04 LTS / 22.04 LTS (hoặc tương tự Debian-based)
- **Python**: Python 3.8+ (3.10+ recommended)
- **Shell**: Bash 4.0+
- **Permissions**: Agent cần sudo privileges cho một số CIS checks (UFW, auditd, etc.)

### Python Packages
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1️⃣ Setup Agent (One-time)

**Option A: Interactive Setup (Recommended)**
```bash
cd /opt/baseline-monitor
python3 agent/setup.py
```

**Option B: Non-interactive Setup (cho automation)**
```bash
python3 agent/setup.py --backend-url http://backend:8000 --no-interactive
```

Setup wizard sẽ:
- ✅ Auto-detect hostname, IP, OS, MAC address
- ✅ Generate `config.yaml` với thông tin Ubuntu machine này
- ✅ Test connection tới backend
- ✅ Sẵn sàng để chạy agent

### 2️⃣ Run Agent

```bash
cd /opt/baseline-monitor
python3 agent/linux/main.py
```

Agent sẽ:
1. ✅ Auto-register với backend (UPSERT by hostname)
2. ✅ Scan 10 Ubuntu CIS Benchmark rules
3. ✅ Report violations tới backend
4. ✅ Send heartbeat mỗi 60 giây
5. ✅ Re-scan mỗi 1 giờ (configurable)

### 3️⃣ Stop Agent

Press `Ctrl+C` để graceful shutdown.

---

## 📁 File Structure

```
agent/linux/
├── __init__.py             # Package init
├── main.py                 # Main agent runner
├── scanner.py              # CIS Benchmark scanner engine
├── shell_executor.py       # Bash command executor
├── rule_loader.py          # Load rules từ JSON
├── violation_reporter.py   # Report violations tới backend
└── README.md               # This file

agent/rules/
└── ubuntu_rules.json       # 10 Ubuntu CIS Benchmark rules
```

---

## 🔍 Ubuntu CIS Rules (10 rules)

| Rule ID | Severity | Category | Description |
|---------|----------|----------|-------------|
| UBU-01 | High | SSH | Disable root SSH login |
| UBU-02 | High | Firewall | Ensure UFW is enabled |
| UBU-03 | Medium | Auditing | Ensure auditd service is enabled |
| UBU-04 | High | System Updates | Ensure automatic updates are enabled |
| UBU-05 | Medium | Password Policy | Set password minimum length >= 14 |
| UBU-06 | Medium | Password Policy | Set password maximum age <= 90 days |
| UBU-07 | High | Filesystem | Ensure /tmp has noexec option |
| UBU-08 | High | Access Control | Ensure AppArmor is enabled |
| UBU-09 | Medium | Logging | Ensure rsyslog service is enabled |
| UBU-10 | Low | Network | Disable IPv6 (if unused) |

---

## 🧪 Testing

### Test Shell Executor (Bash)
```bash
python3 agent/linux/shell_executor.py
```

### Test Rule Loader
```bash
python3 agent/linux/rule_loader.py
```

### Test Scanner
```bash
# Một số rules cần sudo
python3 agent/linux/scanner.py
```

---

## ⚙️ Configuration

File: `config.yaml` (auto-generated bởi setup.py)

```yaml
backend:
  api_url: http://192.168.1.100:8000
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
  max_bytes: 10485760          # 10MB
  backup_count: 5
  console_output: true
```

---

## 🐛 Troubleshooting

### ❌ "Permission Denied" errors
**Cause**: Một số commands cần sudo (UFW, systemctl cho một số services)

**Solution**: 
```bash
# Option 1: Run agent với sudo
sudo python3 agent/linux/main.py

# Option 2: Configure passwordless sudo cho specific commands
sudo visudo
# Add:
# agent_user ALL=(ALL) NOPASSWD: /usr/bin/ufw status
# agent_user ALL=(ALL) NOPASSWD: /bin/systemctl is-enabled *
```

### ❌ Backend Connection Failed
**Solution**:
1. Check backend is running: `curl http://backend:8000/health`
2. Check firewall: `sudo ufw status`
3. Check `config.yaml` có đúng backend URL không

### ❌ Rules Failed với "Command not found"
**Cause**: Thiếu packages

**Solution**: 
```bash
# Install required packages
sudo apt update
sudo apt install -y ufw auditd unattended-upgrades rsyslog apparmor-utils

# Enable services
sudo systemctl enable --now ufw
sudo systemctl enable --now auditd
sudo systemctl enable --now rsyslog
```

### ❌ AppArmor check fails
**Cause**: AppArmor chưa được enable

**Solution**: 
```bash
# Check status
sudo aa-status

# Enable AppArmor
sudo systemctl enable --now apparmor
sudo systemctl start apparmor
```

---

## 🔒 Security Notes

### Sudo Privileges
Agent **cần** sudo để:
- ✅ Check UFW status (`sudo ufw status`)
- ✅ Check service status cho một số services
- ✅ Read protected config files
- ❌ **KHÔNG** modify system settings (chỉ read-only)

### Network Access
Agent **cần** outbound HTTPS tới:
- ✅ Backend API (port 8000 default)
- ❌ **KHÔNG** cần inbound connections

### Data Collected
Agent chỉ gửi:
- ✅ System info (hostname, IP, OS, version)
- ✅ Scan results (PASS/FAIL/ERROR)
- ✅ Violation details (command output, not full logs)
- ❌ **KHÔNG** gửi sensitive data (passwords, credentials, files)

---

## 📊 Monitoring

### View Agent Status
```bash
# Check agent logs
tail -f logs/agent.log

# Check if agent is running
ps aux | grep "agent/linux/main.py"

# Check system resources
top -p $(pgrep -f "agent/linux/main.py")
```

### Backend Status
```bash
# Check agent tại backend
curl http://backend:8000/api/v1/agents

# Check violations của agent này
curl http://backend:8000/api/v1/agents/{agent_id}/violations
```

---

## 🚀 Production Deployment

### 1️⃣ Install as Systemd Service

Create `/etc/systemd/system/baseline-monitor-agent.service`:

```ini
[Unit]
Description=Baseline Monitor Agent - CIS Compliance Scanner
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/baseline-monitor
ExecStart=/usr/bin/python3 /opt/baseline-monitor/agent/linux/main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/baseline-monitor-agent.log
StandardError=append:/var/log/baseline-monitor-agent-error.log

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable baseline-monitor-agent
sudo systemctl start baseline-monitor-agent
sudo systemctl status baseline-monitor-agent
```

### 2️⃣ Configure Scan Interval

Edit `config.yaml`:
```yaml
scanner:
  scan_interval: 3600  # Scan mỗi 1 giờ (3600s)
  # scan_interval: 21600  # Scan mỗi 6 giờ
  # scan_interval: 86400  # Scan mỗi ngày
```

### 3️⃣ Log Rotation

Create `/etc/logrotate.d/baseline-monitor-agent`:

```
/var/log/baseline-monitor-agent*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
```

---

## 🛠️ Advanced Usage

### Run Scan Manually (without agent loop)
```bash
cd /opt/baseline-monitor
python3 -c "
from agent.linux.scanner import run_scan
result = run_scan(agent_id=999, rules_path='agent/rules/ubuntu_rules.json')
print(result.summary())
"
```

### Test Single Rule
```bash
# Test UBU-01 (SSH root login)
grep '^PermitRootLogin' /etc/ssh/sshd_config

# Test UBU-02 (UFW)
sudo ufw status

# Test UBU-03 (auditd)
systemctl is-enabled auditd
```

### Debug Mode
```bash
# Enable DEBUG logging
export LOG_LEVEL=DEBUG
python3 agent/linux/main.py
```

---

## 📚 See Also

- [Project README](../../README.md) - Tổng quan dự án
- [Quick Start Guide](../../docs/QUICK_START.md) - Setup guide chi tiết
- [Windows Agent](../windows/README.md) - Agent cho Windows
- [Selected Rules](../rules/README.md) - Chi tiết về 10 Ubuntu CIS rules

---

## 💡 Tips

1. **Test trước khi deploy production**: Chạy scan thủ công để ensure không có false positives
2. **Monitor logs thường xuyên**: `tail -f logs/agent.log`
3. **Update rules theo nhu cầu**: Edit `ubuntu_rules.json` nếu cần customize
4. **Backup config**: Backup `config.yaml` và `.agent_cache.json` khi migrate
5. **Use Ansible/Puppet**: Deploy agent via automation tools cho nhiều servers

---

## 🔧 Development

### Run Tests
```bash
# Test all components
python3 agent/linux/shell_executor.py
python3 agent/linux/rule_loader.py
python3 agent/linux/scanner.py
python3 agent/linux/violation_reporter.py
```

### Add Custom Rules
1. Edit `agent/rules/ubuntu_rules.json`
2. Add new rule với format:
```json
{
  "id": "UBU-11",
  "name": "Your custom rule",
  "description": "Description",
  "audit_command": "your-command",
  "expected_output": "expected-value",
  "severity": "medium",
  "remediation": "how to fix"
}
```
3. Test: `python3 agent/linux/scanner.py`

---

**Made with ❤️ for CIS Benchmark compliance monitoring**
