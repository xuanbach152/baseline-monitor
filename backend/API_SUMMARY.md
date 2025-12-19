# Backend API Summary - Baseline Monitor

> **Base URL**: `http://localhost:8000/api/v1`
> **WebSocket URL**: `ws://localhost:8000/api/v1/ws`

## 📋 Table of Contents
- [For Agents](#for-agents-monitoring-hosts)
- [For Frontend](#for-frontend-dashboard)
- [Real-time Updates](#real-time-updates-websocket)

---

## 🤖 For Agents (Monitoring Hosts)

### 1. Agent Registration & Heartbeat

#### Register New Agent
```http
POST /api/v1/agents/
Content-Type: application/json

{
  "hostname": "server-01",
  "ip_address": "192.168.1.100",
  "os": "Ubuntu 22.04",
  "version": "1.0.0"
}
```

#### Send Heartbeat
```http
POST /api/v1/agents/{agent_id}/heartbeat
Content-Type: application/json

{
  "is_online": true,
  "compliance_rate": 95.5,
  "last_scan_at": "2025-12-10T10:30:00Z"
}
```

### 2. Get Active Rules

#### Get All Active Rules
```http
GET /api/v1/rules/?active=true
```

#### Get Rule by Agent Rule ID (e.g., "UBU-01", "WIN-03")
```http
GET /api/v1/rules/agent/{agent_rule_id}
```
Example: `/api/v1/rules/agent/UBU-01`

### 3. Report Violations

#### Create Single Violation
```http
POST /api/v1/violations/from-agent
Content-Type: application/json

{
  "agent_id": 1,
  "agent_rule_id": "UBU-01",
  "message": "SSH root login is enabled",
  "confidence_score": 1.0
}
```

#### Bulk Create Violations
```http
POST /api/v1/agents/{agent_id}/violations/bulk
Content-Type: application/json

{
  "violations": [
    {
      "agent_rule_id": "UBU-01",
      "message": "SSH root login enabled",
      "confidence_score": 1.0
    },
    {
      "agent_rule_id": "UBU-02",
      "message": "Firewall not configured",
      "confidence_score": 0.95
    }
  ]
}
```

---

## 🖥️ For Frontend (Dashboard)

### 1. Dashboard Statistics

#### Get Agent Statistics
```http
GET /api/v1/agents/stats

Response:
{
  "total": 10,
  "online": 8,
  "offline": 2
}
```

#### Get Violation Statistics
```http
GET /api/v1/violations/stats

Response:
{
  "total": 150,
  "resolved": 100,
  "unresolved": 50,
  "by_severity": {
    "critical": 10,
    "high": 30,
    "medium": 60,
    "low": 50
  }
}
```

#### Get Violation Count
```http
GET /api/v1/violations/stats/count?resolved=false

Response:
{
  "count": 50
}
```

#### Get Violations by Severity
```http
GET /api/v1/violations/stats/by-severity

Response:
[
  {"severity": "critical", "count": 10},
  {"severity": "high", "count": 30},
  {"severity": "medium", "count": 60},
  {"severity": "low", "count": 50}
]
```

#### Get Violations by Agent
```http
GET /api/v1/violations/stats/by-agent

Response:
[
  {"agent_id": 1, "hostname": "server-01", "count": 25},
  {"agent_id": 2, "hostname": "server-02", "count": 15}
]
```

#### Get Recent Violations Count (Last 24h)
```http
GET /api/v1/violations/stats/recent-count?hours=24

Response:
{
  "count": 15,
  "hours": 24
}
```

#### Get 7-Day Trend
```http
GET /api/v1/violations/stats/7day-trend

Response:
[
  {"date": "2025-12-04", "count": 10},
  {"date": "2025-12-05", "count": 15},
  {"date": "2025-12-06", "count": 8},
  ...
]
```

#### Get Top 5 Recent Violations
```http
GET /api/v1/violations/stats/top-5-recent

Response: [Array of 5 most recent violations]
```

### 2. Agents Management

#### List All Agents
```http
GET /api/v1/agents/
Query params: skip=0, limit=100, is_online=true, os=Ubuntu
```

#### Get Agent Details
```http
GET /api/v1/agents/{agent_id}
```

#### Update Agent
```http
PUT /api/v1/agents/{agent_id}
Content-Type: application/json

{
  "hostname": "server-01-updated",
  "is_online": false
}
```

#### Delete Agent
```http
DELETE /api/v1/agents/{agent_id}
```

#### Get Agent Violations
```http
GET /api/v1/agents/{agent_id}/violations?limit=100
```

### 3. Rules Management

#### List All Rules
```http
GET /api/v1/rules/
Query params: skip=0, limit=100, active=true, severity=high, os_type=linux
```

#### Get Rule Details
```http
GET /api/v1/rules/{rule_id}
```

#### Create Rule
```http
POST /api/v1/rules/
Content-Type: application/json

{
  "name": "SSH Root Login Disabled",
  "description": "Ensure SSH root login is disabled",
  "check_expression": "grep PermitRootLogin /etc/ssh/sshd_config",
  "severity": "high",
  "category": "authentication",
  "os_type": "linux",
  "agent_rule_id": "UBU-01",
  "active": true
}
```

#### Update Rule
```http
PUT /api/v1/rules/{rule_id}
Content-Type: application/json

{
  "severity": "critical",
  "active": false
}
```

#### Toggle Rule Active/Inactive
```http
PATCH /api/v1/rules/{rule_id}/toggle
```

#### Delete Rule
```http
DELETE /api/v1/rules/{rule_id}
```

### 4. Violations Management

#### List All Violations
```http
GET /api/v1/violations/
Query params: 
  - skip=0
  - limit=100
  - agent_id=1
  - rule_id=5
  - severity=high
  - resolved=false
  - date_from=2025-12-01
  - date_to=2025-12-10
```

#### Get Recent Violations
```http
GET /api/v1/violations/recent?limit=20
```

#### Get Violation Details
```http
GET /api/v1/violations/{violation_id}
```

#### Get Violations by Agent
```http
GET /api/v1/violations/agent/{agent_id}?limit=100
```

#### Get Violations by Rule
```http
GET /api/v1/violations/rule/{rule_id}?limit=100
```

#### Resolve Violation
```http
PUT /api/v1/violations/{violation_id}
Content-Type: application/json

{
  "resolved_at": "2025-12-10T15:30:00Z",
  "resolved_by": "admin",
  "resolution_notes": "Fixed SSH configuration and restarted service"
}
```

#### Delete Violation
```http
DELETE /api/v1/violations/{violation_id}
```

#### Delete All Violations for Agent
```http
DELETE /api/v1/violations/agent/{agent_id}/all
```

### 5. Reports Export

#### Generate PDF Report
```http
GET /api/v1/reports/compliance/pdf
Query params:
  - date_from=2025-11-10 (optional, default: 30 days ago)
  - date_to=2025-12-10 (optional, default: today)

Response: PDF file download
```

#### Export Violations to CSV
```http
GET /api/v1/reports/violations/csv
Query params:
  - date_from=2025-11-10
  - date_to=2025-12-10
  - severity=high (optional)
  - resolved=false (optional)

Response: CSV file download
```

#### Export Violations to Excel
```http
GET /api/v1/reports/violations/excel
Query params:
  - date_from=2025-11-10
  - date_to=2025-12-10
  - severity=critical (optional)
  - resolved=true (optional)

Response: Excel (.xlsx) file download
```

### 6. Users Management

#### Create User
```http
POST /api/v1/users/
Content-Type: application/json

{
  "username": "admin",
  "email": "admin@example.com",
  "password": "securepassword",
  "full_name": "System Administrator"
}
```

#### List Users
```http
GET /api/v1/users/
Query params: skip=0, limit=100, is_active=true
```

#### Get User Details
```http
GET /api/v1/users/{user_id}
```

#### Update User
```http
PUT /api/v1/users/{user_id}
Content-Type: application/json

{
  "full_name": "Updated Name",
  "is_active": false
}
```

#### Delete User
```http
DELETE /api/v1/users/{user_id}
```

#### User Login
```http
POST /api/v1/users/login
Content-Type: application/json

{
  "username": "admin",
  "password": "securepassword"
}
```

---

## 🔄 Real-time Updates (WebSocket)

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws');

ws.onopen = () => {
  console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Keep connection alive
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping' }));
}, 30000);
```

### Events Broadcasted

#### 1. Violation Events
```javascript
// New violation detected
{
  "event": "violation_created",
  "data": {
    "id": 123,
    "agent_id": 1,
    "rule_id": 5,
    "message": "SSH root login enabled",
    "confidence_score": 1.0,
    "detected_at": "2025-12-10T10:30:00Z"
  }
}

// Violation resolved
{
  "event": "violation_resolved",
  "data": {
    "id": 123,
    "resolved_by": "admin",
    "resolved_at": "2025-12-10T15:30:00Z"
  }
}

// Violation deleted
{
  "event": "violation_deleted",
  "data": {
    "id": 123
  }
}
```

#### 2. Agent Events
```javascript
// Agent status changed
{
  "event": "agent_status_changed",
  "data": {
    "agent_id": 1,
    "hostname": "server-01",
    "is_online": false
  }
}

// Agent updated
{
  "event": "agent_updated",
  "data": {
    "id": 1,
    "hostname": "server-01-updated",
    "ip_address": "192.168.1.100",
    "os": "Ubuntu 22.04",
    "version": "1.0.0",
    "is_online": true
  }
}

// Agent deleted
{
  "event": "agent_deleted",
  "data": {
    "agent_id": "1"
  }
}
```

#### 3. Rule Events
```javascript
// Rule updated
{
  "event": "rule_updated",
  "data": {
    "id": 5,
    "name": "SSH Root Login Disabled",
    "severity": "critical",
    "is_active": true
  }
}

// Rule toggled
{
  "event": "rule_toggled",
  "data": {
    "id": 5,
    "name": "SSH Root Login Disabled",
    "is_active": false
  }
}

// Rule deleted
{
  "event": "rule_deleted",
  "data": {
    "rule_id": "5"
  }
}
```

---

## 📊 Database Tables

Current database schema (4 core tables):

1. **users** - User accounts
2. **agents** - Monitored hosts
3. **rules** - CIS compliance rules
4. **violations** - Detected violations
5. **alembic_version** - Migration tracking

---

## 🔧 Tech Stack

- **Framework**: FastAPI 0.115.5
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: WebSocket
- **Reports**: ReportLab (PDF), Pandas (CSV), OpenPyXL (Excel)
- **Migration**: Alembic

---

## 📝 Notes

### For Agent Development:
1. Register agent on startup
2. Fetch active rules periodically (e.g., every 5 minutes)
3. Run compliance checks based on `check_expression`
4. Report violations via `/from-agent` or bulk endpoint
5. Send heartbeat every 30-60 seconds

### For Frontend Development:
1. Connect to WebSocket on app load
2. Fetch statistics for dashboard charts
3. Use real-time events to update UI without polling
4. Implement filters for violations list
5. Use export endpoints for download features

### API Design Principles:
- RESTful conventions
- Consistent response formats
- Real-time updates via WebSocket
- Filter support on list endpoints
- Proper HTTP status codes
- Comprehensive error messages
