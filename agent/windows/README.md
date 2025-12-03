# Windows Agent - Baseline Monitor

Windows CIS Benchmark Compliance Agent với auto-registration và real-time scanning.

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11 (Pro/Enterprise)
- **Python**: Python 3.8+ (3.10+ recommended)
- **PowerShell**: PowerShell 5.1+ (built-in on Windows 10/11)
- **Administrator**: Agent cần chạy với quyền Administrator để execute một số CIS checks

### Python Packages
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1️⃣ Setup Agent (One-time)

**Option A: Interactive Setup (Recommended)**
```powershell
# Open PowerShell as Administrator
cd C:\baseline-monitor
python agent\setup.py
```

**Option B: Non-interactive Setup (cho automation)**
```powershell
python agent\setup.py --backend-url http://backend:8000 --no-interactive
```

Setup wizard sẽ:
- ✅ Auto-detect hostname, IP, OS, MAC address
- ✅ Generate `config.yaml` với thông tin Windows machine này
- ✅ Test connection tới backend
- ✅ Sẵn sàng để chạy agent

### 2️⃣ Run Agent

```powershell
# Open PowerShell as Administrator
cd C:\baseline-monitor
python agent\windows\main.py
```

Agent sẽ:
1. ✅ Auto-register với backend (UPSERT by hostname)
2. ✅ Scan 10 Windows CIS Benchmark rules
3. ✅ Report violations tới backend
4. ✅ Send heartbeat mỗi 60 giây
5. ✅ Re-scan mỗi 1 giờ (configurable)

### 3️⃣ Stop Agent

Press `Ctrl+C` để graceful shutdown.

---

## 📁 File Structure

```
agent/windows/
├── main.py                 # Main agent runner
├── scanner.py              # CIS Benchmark scanner engine
├── shell_executor.py       # PowerShell command executor
├── rule_loader.py          # Load rules từ JSON
├── violation_reporter.py   # Report violations tới backend
└── README.md               # This file

agent/rules/
└── windows_rules.json      # 10 Windows CIS Benchmark rules
```

---

## 🔍 Windows CIS Rules (10 rules)

| Rule ID | Severity | Category | Description |
|---------|----------|----------|-------------|
| WIN-01 | High | Network | Disable SMBv1 protocol |
| WIN-02 | Critical | Antivirus | Ensure Windows Defender is enabled |
| WIN-03 | High | Firewall | Ensure Firewall is enabled for all profiles |
| WIN-04 | Medium | Password Policy | Set Account lockout threshold <= 5 |
| WIN-05 | Medium | Password Policy | Set password minimum length >= 14 |
| WIN-06 | Medium | Password Policy | Set password maximum age <= 90 days |
| WIN-07 | High | Access Control | Enable User Account Control (UAC) |
| WIN-08 | Medium | Auditing | Enable Audit Logon Events |
| WIN-09 | Medium | Network | Disable Remote Desktop (if unused) |
| WIN-10 | High | System Updates | Ensure Automatic Updates are enabled |

---

## 🧪 Testing

### Test Shell Executor (PowerShell)
```powershell
python agent\windows\shell_executor.py
```

### Test Rule Loader
```powershell
python agent\windows\rule_loader.py
```

### Test Scanner
```powershell
# Chạy với Administrator privileges!
python agent\windows\scanner.py
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
  hostname: WIN-DESKTOP-01
  os_type: windows

scanner:
  scan_interval: 3600          # Scan mỗi 1 giờ
  rules_path: ./agent/rules/windows_rules.json
  command_timeout: 30
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

### ❌ "Access Denied" errors
**Solution**: Run PowerShell as **Administrator**

```powershell
# Right-click PowerShell → "Run as Administrator"
```

### ❌ PowerShell Execution Policy
**Error**: "cannot be loaded because running scripts is disabled"

**Solution**: 
```powershell
# Temporary fix (cho session hiện tại)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Hoặc permanent (khuyên dùng RemoteSigned)
Set-ExecutionPolicy RemoteSigned -Force
```

### ❌ Backend Connection Failed
**Solution**:
1. Check backend is running: `curl http://backend:8000/health`
2. Check firewall: Allow port 8000
3. Check `config.yaml` có đúng backend URL không

### ❌ Rules Failed với "Command not found"
**Cause**: Một số PowerShell commands cần modules hoặc features

**Solution**: 
```powershell
# Check PowerShell version
$PSVersionTable.PSVersion

# Update PowerShell nếu < 5.1
# Download từ: https://aka.ms/pswindows
```

### ❌ "Windows Defender" checks fail
**Cause**: Windows Defender bị disable hoặc dùng third-party antivirus

**Solution**: 
- Nếu dùng third-party AV → Expected behavior (rule sẽ FAIL)
- Nếu cần enable Defender:
  ```powershell
  Set-MpPreference -DisableRealtimeMonitoring $false
  ```

---

## 🔒 Security Notes

### Administrator Privileges
Agent **cần** Administrator để:
- ✅ Execute `auditpol` commands (WIN-08)
- ✅ Read Registry keys (WIN-07, WIN-09)
- ✅ Check Firewall profiles (WIN-03)
- ✅ Get Windows features (WIN-01)

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
```powershell
# Check agent logs
Get-Content logs\agent.log -Tail 50 -Wait

# Check if agent is running
Get-Process -Name python | Where-Object { $_.CommandLine -like "*agent\windows\main.py*" }
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

### 1️⃣ Install as Windows Service

**Option A: NSSM (Non-Sucking Service Manager)**
```powershell
# Download NSSM từ: https://nssm.cc/download
nssm install BaselineMonitorAgent "C:\Python310\python.exe" "C:\baseline-monitor\agent\windows\main.py"
nssm set BaselineMonitorAgent AppDirectory "C:\baseline-monitor"
nssm set BaselineMonitorAgent DisplayName "Baseline Monitor Agent"
nssm set BaselineMonitorAgent Description "CIS Benchmark Compliance Agent"
nssm start BaselineMonitorAgent
```

**Option B: Task Scheduler**
```powershell
# Create scheduled task to run at startup
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\baseline-monitor\agent\windows\main.py" -WorkingDirectory "C:\baseline-monitor"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "BaselineMonitorAgent" -Action $action -Trigger $trigger -Principal $principal
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

Logs tự động rotate khi đạt 10MB (configurable trong `config.yaml`).

---

## 📚 See Also

- [Project README](../../README.md) - Tổng quan dự án
- [Quick Start Guide](../../docs/QUICK_START.md) - Setup guide chi tiết
- [Linux Agent](../linux/README.md) - Agent cho Ubuntu/Linux
- [Selected Rules](../rules/README.md) - Chi tiết về 10 Windows CIS rules

---

## 💡 Tips

1. **Test trước khi deploy production**: Chạy scan thủ công để ensure không có false positives
2. **Monitor logs thường xuyên**: Check `logs/agent.log` để catch errors sớm
3. **Update rules theo nhu cầu**: Edit `windows_rules.json` nếu cần customize
4. **Backup config**: Backup `config.yaml` và `.agent_cache.json` khi migrate
5. **Use Group Policy**: Deploy agent via GPO cho nhiều máy cùng lúc

---

**Made with ❤️ for CIS Benchmark compliance monitoring**
