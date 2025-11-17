# Ubuntu Rules - Chi Tiết Và So Sánh Với Backend Database

## 📊 KIẾN TRÚC 2 LỚP RULES

```
┌─────────────────────────────────────────────────────────────┐
│                    BASELINE MONITOR                         │
│                                                             │
│  ┌──────────────────┐              ┌──────────────────┐   │
│  │   AGENT SIDE     │              │   BACKEND SIDE   │   │
│  │  (Local Files)   │              │   (Database)     │   │
│  └──────────────────┘              └──────────────────┘   │
│           │                                  │              │
│           ▼                                  ▼              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ubuntu_rules.json (10 rules)                       │  │
│  │  ┌────────────────────────────────────────────┐     │  │
│  │  │ • id: "UBU-01" (String)                    │     │  │
│  │  │ • audit_command: Shell command             │     │  │
│  │  │ • expected_output: What to expect          │     │  │
│  │  │ • remediation: How to fix                  │     │  │
│  │  └────────────────────────────────────────────┘     │  │
│  │                                                      │  │
│  │  MỤC ĐÍCH:                                           │  │
│  │  - Agent đọc file này LOCAL                          │  │
│  │  - Chạy audit_command trên máy client                │  │
│  │  - So sánh output với expected_output                │  │
│  │  - Tự động detect PASS/FAIL                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  rules table (PostgreSQL)                           │  │
│  │  ┌────────────────────────────────────────────┐     │  │
│  │  │ • id: 1, 2, 3... (Integer, auto-increment) │     │  │
│  │  │ • name: "Disable root SSH login"           │     │  │
│  │  │ • check_expression: Nullable               │     │  │
│  │  │ • severity: low/medium/high/critical       │     │  │
│  │  │ • active: true/false                       │     │  │
│  │  └────────────────────────────────────────────┘     │  │
│  │                                                      │  │
│  │  MỤC ĐÍCH:                                           │  │
│  │  - Backend quản lý metadata                          │  │
│  │  - Frontend hiển thị danh sách rules                 │  │
│  │  - Link với violations table (Foreign Key)          │  │
│  │  - Admin enable/disable rules                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 SO SÁNH CHI TIẾT 2 LỚP RULES

### 1. **Agent Rules (ubuntu_rules.json)** - Execution Layer

**Location:** `agent/rules/ubuntu_rules.json`

**Format:** JSON Array

**Mục đích:** 
- Chứa **LOGIC THỰC THI** của mỗi rule
- Agent đọc file này để biết **LÀM GÌ** và **KỲ VỌNG GÌ**
- Tự động detect compliance mà KHÔNG CẦN gọi backend

**Schema:**
```json
{
  "id": "UBU-01",                    // String ID (unique identifier)
  "name": "Disable root SSH login",  // Human-readable name
  "description": "...",              // Chi tiết mục đích
  "audit_command": "grep ...",       // Shell command to check
  "expected_output": "...",          // What output means PASS
  "severity": "high",                // Importance level
  "remediation": "..."               // How to fix if FAIL
}
```

**Đặc điểm:**
- ✅ **String ID** (`"UBU-01"`) - dễ nhận diện, không thay đổi
- ✅ **audit_command** - shell command thực tế
- ✅ **expected_output** - để agent tự động so sánh
- ✅ **remediation** - hướng dẫn fix (optional, cho logs)
- ✅ **Độc lập** - agent hoạt động offline, không cần backend
- ⚠️ **Phải seed vào backend** - để backend biết rule_id khi agent report violation

---

### 2. **Backend Rules (Database)** - Management Layer

**Location:** PostgreSQL table `rules`

**Schema:**
```sql
CREATE TABLE rules (
    id SERIAL PRIMARY KEY,              -- Integer auto-increment
    name VARCHAR NOT NULL,              -- "Disable root SSH login"
    description TEXT,                   -- Detailed explanation
    check_expression TEXT,              -- Nullable (not used by agent)
    severity VARCHAR DEFAULT 'medium',  -- low/medium/high/critical
    active BOOLEAN DEFAULT TRUE         -- Enable/disable rule
);
```

**Mục đích:**
- Quản lý **METADATA** của rules
- Link với **violations table** (Foreign Key)
- Frontend hiển thị danh sách rules
- Admin enable/disable rules qua API

**Đặc điểm:**
- ✅ **Integer ID** (1, 2, 3...) - database auto-increment
- ✅ **check_expression** - nullable, có thể bỏ trống
- ✅ **active flag** - admin có thể tắt rule
- ⚠️ **KHÔNG chứa audit_command** - backend không execute
- ⚠️ **KHÔNG chứa expected_output** - backend không detect

---

## 🔗 MỐI QUAN HỆ GIỮA 2 LỚP

### Workflow:

```
1. AGENT SCAN (Local)
   ┌─────────────────────────────────────────┐
   │ Agent reads ubuntu_rules.json           │
   │ → For each rule:                        │
   │   - Execute audit_command               │
   │   - Compare output vs expected_output   │
   │   - Detect: PASS / FAIL / ERROR         │
   └─────────────────────────────────────────┘
                    │
                    ▼ (Only report FAIL)
   ┌─────────────────────────────────────────┐
   │ POST /api/v1/violations                 │
   │ {                                        │
   │   "agent_id": 7,                         │
   │   "rule_id": "UBU-01",   ← String!      │
   │   "message": "Expected 'no', got 'yes'" │
   │ }                                        │
   └─────────────────────────────────────────┘
                    │
                    ▼
2. BACKEND PROCESSING
   ┌─────────────────────────────────────────┐
   │ Backend receives violation              │
   │ → Lookup rule_id "UBU-01" in DB         │
   │ → Get integer ID (e.g., 1)              │
   │ → Save to violations table:             │
   │   {                                      │
   │     agent_id: 7,                         │
   │     rule_id: 1,         ← Integer FK!   │
   │     message: "...",                      │
   │     detected_at: now()                   │
   │   }                                      │
   └─────────────────────────────────────────┘
                    │
                    ▼
3. FRONTEND DISPLAY
   ┌─────────────────────────────────────────┐
   │ GET /api/v1/violations?agent_id=7       │
   │ → JOIN violations + rules tables        │
   │ → Return:                                │
   │   {                                      │
   │     "rule": {                            │
   │       "id": 1,                           │
   │       "name": "Disable root SSH login", │
   │       "severity": "high"                 │
   │     },                                   │
   │     "message": "...",                    │
   │     "detected_at": "..."                 │
   │   }                                      │
   └─────────────────────────────────────────┘
```

---

## 📝 CHI TIẾT TỪNG RULE

### **UBU-01: Disable root SSH login**

**Agent Side (ubuntu_rules.json):**
```json
{
  "id": "UBU-01",
  "name": "Disable root SSH login",
  "description": "Prevent direct root login via SSH to reduce attack surface. Root access should only be obtained through sudo after regular user login.",
  "audit_command": "grep '^PermitRootLogin' /etc/ssh/sshd_config",
  "expected_output": "PermitRootLogin no",
  "severity": "high",
  "remediation": "Edit /etc/ssh/sshd_config and set 'PermitRootLogin no', then run 'sudo systemctl restart sshd'"
}
```

**Giải thích:**
- **Mục đích:** Ngăn chặn login trực tiếp bằng tài khoản root qua SSH
- **Tại sao quan trọng:** Root có toàn quyền hệ thống, nếu bị brute-force sẽ rất nguy hiểm
- **Logic check:** Tìm dòng `PermitRootLogin` trong sshd_config, kỳ vọng giá trị là `no`
- **Agent behavior:**
  - Chạy: `grep '^PermitRootLogin' /etc/ssh/sshd_config`
  - Nếu output chứa `"PermitRootLogin no"` → **PASS** ✅
  - Nếu output khác (hoặc không có) → **FAIL** ❌
  - Nếu lỗi (file không tồn tại) → **ERROR** ⚠️

**Backend Side (rules table):**
```sql
INSERT INTO rules (name, description, severity, active)
VALUES (
  'Disable root SSH login',
  'Prevent direct root login via SSH',
  'high',
  true
);
-- Returns id = 1
```

**Link:** Khi agent report violation với `rule_id="UBU-01"`, backend lookup và map sang `id=1`

---

### **UBU-02: Ensure UFW is enabled**

**Agent Side:**
```json
{
  "id": "UBU-02",
  "name": "Ensure UFW is enabled",
  "description": "Enable Uncomplicated Firewall (UFW) to provide host-based firewall protection and control network traffic.",
  "audit_command": "sudo ufw status",
  "expected_output": "Status: active",
  "severity": "high",
  "remediation": "Run 'sudo ufw enable' to activate the firewall"
}
```

**Giải thích:**
- **Mục đích:** Bật firewall để kiểm soát traffic in/out
- **Tại sao quan trọng:** Firewall là lớp bảo vệ đầu tiên chống lại network attacks
- **Logic check:** 
  - Chạy `sudo ufw status`
  - Kỳ vọng output chứa `"Status: active"`
  - Nếu thấy `"Status: inactive"` → **FAIL**

**Lưu ý:** Agent cần chạy với sudo privileges hoặc config NOPASSWD cho lệnh `ufw status`

---

### **UBU-03: Ensure auditd service is enabled**

**Agent Side:**
```json
{
  "id": "UBU-03",
  "name": "Ensure auditd service is enabled",
  "description": "Enable audit daemon (auditd) to track security-relevant events for compliance and forensic analysis.",
  "audit_command": "systemctl is-enabled auditd",
  "expected_output": "enabled",
  "severity": "medium",
  "remediation": "Run 'sudo apt install auditd -y && sudo systemctl enable --now auditd'"
}
```

**Giải thích:**
- **Mục đích:** Bật auditd để log các security events (login, file access, etc.)
- **Tại sao quan trọng:** Compliance requirements (HIPAA, PCI-DSS) yêu cầu audit logging
- **Logic check:** 
  - `systemctl is-enabled auditd` return `"enabled"` → **PASS**
  - Return `"disabled"` → **FAIL**
  - Service không tồn tại → **ERROR**

---

### **UBU-04: Ensure automatic updates are enabled**

**Agent Side:**
```json
{
  "id": "UBU-04",
  "name": "Ensure automatic updates are enabled",
  "description": "Enable unattended-upgrades to automatically install security patches and keep the system up-to-date.",
  "audit_command": "systemctl is-enabled unattended-upgrades",
  "expected_output": "enabled",
  "severity": "high",
  "remediation": "Run 'sudo apt install unattended-upgrades -y && sudo systemctl enable --now unattended-upgrades'"
}
```

**Giải thích:**
- **Mục đích:** Tự động cài đặt security patches
- **Tại sao quan trọng:** 90% exploits lợi dụng vulnerabilities đã có patch
- **Severity: HIGH** vì unpatched systems là mục tiêu dễ nhất cho attackers

---

### **UBU-05: Set password minimum length >= 14**

**Agent Side:**
```json
{
  "id": "UBU-05",
  "name": "Set password minimum length >= 14",
  "description": "Enforce strong password policy by requiring minimum password length of 14 characters to resist brute-force attacks.",
  "audit_command": "grep '^PASS_MIN_LEN' /etc/login.defs",
  "expected_output": "PASS_MIN_LEN\t14",
  "severity": "medium",
  "remediation": "Edit /etc/login.defs and set 'PASS_MIN_LEN 14'"
}
```

**Giải thích:**
- **Mục đích:** Enforce mật khẩu mạnh (>= 14 ký tự)
- **Tại sao 14:** NIST recommends minimum 14 characters for passwords
- **Logic check:** 
  - Tìm dòng `PASS_MIN_LEN` trong `/etc/login.defs`
  - Kỳ vọng giá trị >= 14
  - Lưu ý: expected_output có `\t` (tab character)

---

### **UBU-06: Set password maximum age <= 90 days**

**Agent Side:**
```json
{
  "id": "UBU-06",
  "name": "Set password maximum age <= 90 days",
  "description": "Enforce periodic password changes by setting maximum password age to 90 days or less.",
  "audit_command": "grep '^PASS_MAX_DAYS' /etc/login.defs",
  "expected_output": "PASS_MAX_DAYS\t90",
  "severity": "medium",
  "remediation": "Edit /etc/login.defs and set 'PASS_MAX_DAYS 90'"
}
```

**Giải thích:**
- **Mục đích:** Buộc user đổi password định kỳ
- **Tại sao 90 days:** Balance giữa security và usability
- **Compliance:** PCI-DSS requires password expiration <= 90 days

---

### **UBU-07: Ensure /tmp has noexec option**

**Agent Side:**
```json
{
  "id": "UBU-07",
  "name": "Ensure /tmp has noexec option",
  "description": "Prevent execution of binaries in /tmp directory to mitigate malware execution from temporary files.",
  "audit_command": "findmnt -n /tmp | grep noexec",
  "expected_output": "noexec",
  "severity": "high",
  "remediation": "Add 'noexec' option to /tmp mount in /etc/fstab and run 'sudo mount -o remount /tmp'"
}
```

**Giải thích:**
- **Mục đích:** Ngăn chặn execute binaries trong /tmp
- **Tại sao quan trọng:** Malware thường download vào /tmp rồi execute
- **Logic check:**
  - `findmnt -n /tmp` hiển thị mount options
  - `grep noexec` tìm option noexec
  - Nếu không thấy → **FAIL** (có thể execute trong /tmp)

**Severity: HIGH** vì đây là defense-in-depth layer quan trọng

---

### **UBU-08: Ensure AppArmor is enabled**

**Agent Side:**
```json
{
  "id": "UBU-08",
  "name": "Ensure AppArmor is enabled",
  "description": "Enable AppArmor for mandatory access control to confine programs and limit potential damage from security breaches.",
  "audit_command": "aa-status 2>/dev/null | grep -q 'apparmor module is loaded' && echo 'loaded' || echo 'not loaded'",
  "expected_output": "loaded",
  "severity": "high",
  "remediation": "Run 'sudo systemctl enable --now apparmor' and reboot if necessary"
}
```

**Giải thích:**
- **Mục đích:** Bật AppArmor (Mandatory Access Control)
- **Tại sao quan trọng:** AppArmor confine programs, giới hạn damage nếu bị compromise
- **Logic check:**
  - `aa-status` check AppArmor status
  - `2>/dev/null` bỏ qua errors
  - `grep -q 'apparmor module is loaded'` check module loaded
  - `&& echo 'loaded' || echo 'not loaded'` return status
  - Kỳ vọng: `"loaded"`

**Lưu ý:** Command phức tạp với shell operators (`&&`, `||`)

---

### **UBU-09: Ensure rsyslog service is enabled**

**Agent Side:**
```json
{
  "id": "UBU-09",
  "name": "Ensure rsyslog service is enabled",
  "description": "Enable rsyslog service to collect, process, and forward system log messages for monitoring and troubleshooting.",
  "audit_command": "systemctl is-enabled rsyslog",
  "expected_output": "enabled",
  "severity": "medium",
  "remediation": "Run 'sudo apt install rsyslog -y && sudo systemctl enable --now rsyslog'"
}
```

**Giải thích:**
- **Mục đích:** Bật rsyslog để collect system logs
- **Tại sao quan trọng:** Logs là first line of defense trong incident response
- **Severity: MEDIUM** vì không critical như firewall, nhưng cần cho forensics

---

### **UBU-10: Disable IPv6 (if unused)**

**Agent Side:**
```json
{
  "id": "UBU-10",
  "name": "Disable IPv6 (if unused)",
  "description": "Disable IPv6 protocol if not used to reduce attack surface and prevent IPv6-based attacks.",
  "audit_command": "sysctl net.ipv6.conf.all.disable_ipv6",
  "expected_output": "net.ipv6.conf.all.disable_ipv6 = 1",
  "severity": "low",
  "remediation": "Run 'sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1' and add to /etc/sysctl.conf for persistence"
}
```

**Giải thích:**
- **Mục đích:** Tắt IPv6 nếu không dùng
- **Tại sao:** Giảm attack surface, tránh IPv6-specific attacks
- **Severity: LOW** vì không critical, nhiều hệ thống cần IPv6
- **Logic check:**
  - `sysctl net.ipv6.conf.all.disable_ipv6` return value
  - `= 1` means IPv6 disabled (PASS)
  - `= 0` means IPv6 enabled (FAIL if not used)

---

## ⚠️ VẤN ĐỀ CẦN GIẢI QUYẾT

### **1. ID Mapping: String vs Integer**

**Vấn đề:**
- Agent rules dùng **String ID** (`"UBU-01"`)
- Backend rules dùng **Integer ID** (auto-increment)
- Cần **mapping** khi agent report violation

**Giải pháp:**

#### Option 1: Backend Mapping Table (KHUYẾN NGHỊ)
```sql
CREATE TABLE rule_mappings (
    agent_rule_id VARCHAR(20) PRIMARY KEY,  -- "UBU-01"
    backend_rule_id INTEGER REFERENCES rules(id)
);

INSERT INTO rule_mappings VALUES ('UBU-01', 1);
INSERT INTO rule_mappings VALUES ('UBU-02', 2);
...
```

**Backend logic khi nhận violation:**
```python
# Agent gửi: rule_id = "UBU-01"
agent_rule_id = violation_data.get("rule_id")  # "UBU-01"

# Lookup mapping
backend_rule_id = db.query(RuleMapping).filter_by(
    agent_rule_id=agent_rule_id
).first().backend_rule_id  # 1

# Save với Integer ID
violation = Violation(
    agent_id=7,
    rule_id=backend_rule_id,  # 1
    message=violation_data.get("message")
)
```

#### Option 2: Add String ID Column to Rules Table
```sql
ALTER TABLE rules ADD COLUMN agent_rule_id VARCHAR(20) UNIQUE;
UPDATE rules SET agent_rule_id = 'UBU-01' WHERE id = 1;
```

**Trade-off:**
- ✅ Không cần thêm table
- ❌ Mix String + Integer trong cùng 1 table (không clean)

---

### **2. Seeding Backend Rules**

Backend cần **seed** 10 rules vào database khi setup:

**File:** `backend/alembic/versions/xxx_seed_ubuntu_rules.py`

```python
"""Seed Ubuntu CIS rules

Revision ID: xxx
Revises: f620c806eaee
Create Date: 2025-11-17
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Insert 10 Ubuntu rules
    op.execute("""
        INSERT INTO rules (name, description, severity, active) VALUES
        ('Disable root SSH login', 'Prevent direct root login via SSH', 'high', true),
        ('Ensure UFW is enabled', 'Enable host-based firewall', 'high', true),
        ('Ensure auditd service is enabled', 'Enable security auditing', 'medium', true),
        ('Ensure automatic updates are enabled', 'Keep security patches up-to-date', 'high', true),
        ('Set password minimum length >= 14', 'Enforce strong passwords', 'medium', true),
        ('Set password maximum age <= 90 days', 'Enforce periodic password change', 'medium', true),
        ('Ensure /tmp has noexec option', 'Prevent execution in /tmp', 'high', true),
        ('Ensure AppArmor is enabled', 'Enable process-level protection', 'high', true),
        ('Ensure rsyslog service is enabled', 'Enable system logging', 'medium', true),
        ('Disable IPv6 (if unused)', 'Reduce network attack surface', 'low', true);
    """)

def downgrade():
    op.execute("DELETE FROM rules WHERE name LIKE '%SSH%' OR name LIKE '%UFW%';")
```

Chạy migration:
```bash
cd backend
alembic revision -m "seed_ubuntu_rules"
# Edit file migrations/xxx_seed_ubuntu_rules.py
alembic upgrade head
```

---

## 🎯 NEXT STEPS

1. ✅ **Task 1 COMPLETED:** Created `ubuntu_rules.json`
2. 🎯 **Task 2:** Implement `rule_loader.py` to read JSON
3. 🎯 **Task 3:** Implement `shell_executor.py` to run commands
4. 🎯 **Task 4:** Implement `scanner.py` to detect violations
5. ⚠️ **Backend:** Create migration to seed rules table
6. ⚠️ **Backend:** Add rule_id mapping logic in violations endpoint

---

## 📚 TÀI LIỆU THAM KHẢO

- **CIS Benchmarks:** https://www.cisecurity.org/cis-benchmarks
- **Ubuntu Security Guide:** https://ubuntu.com/security/certifications/docs/
- **NIST Password Guidelines:** https://pages.nist.gov/800-63-3/

---

**Created:** November 17, 2025  
**Author:** GitHub Copilot + Nguyen Xuan Bach  
**Version:** 1.0
