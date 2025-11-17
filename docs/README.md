# 📚 DOCS FOLDER - OVERVIEW

**Purpose:** Essential documentation for Baseline Monitor project

---

## 📋 CURRENT DOCS (10 files)

### ✅ Active Documentation

| File | Purpose | Status |
|------|---------|--------|
| **PROJECT_STRUCTURE.md** | File/folder structure reference | ✅ Complete |
| **QUICK_START.md** | Setup guide (3 ways to install agent) | ✅ Complete |
| **selected_rules.md** | 10 CIS Benchmark rules selected | ✅ Complete |
| **scope.pdf** | Project scope (thesis requirement) | ✅ Complete |

### 📝 Placeholders (To be filled)

| File | Purpose | When |
|------|---------|------|
| **api_spec.md** | Backend API documentation | Auto-generate from FastAPI |
| **architecture.md** | System architecture | TUẦN 7-8 (thesis) |
| **database_schema.md** | Database schema docs | Auto-generate |
| **deployment_guide.md** | Production deployment | TUẦN 5-6 |
| **test_plan.md** | Testing strategy | TUẦN 5-6 |
| **report.md** | Weekly progress reports | Ongoing |

---

## 🗑️ DELETED DOCS (8 files)

**Explanation docs** - chỉ để giải thích code một lần, không cần commit:

- `AGENT_SYSTEM_INFO.md` - Giải thích `system_info.py`
- `AUTO_REGISTRATION.md` - Giải thích auto-registration
- `AUTO_REGISTRATION_DETAIL.md` - Chi tiết registration flow
- `CLEANUP_REPORT.md` - Report cleanup history
- `HTTP_CLIENT_DETAIL.md` - Giải thích `http_client.py`
- `LUONG_AGENT_CHI_TIET.md` - Vietnamese explanation
- `MODELS_COMPARISON.md` - Agent vs Backend models comparison
- `DOCS_CLEANUP_PLAN.md` - Cleanup plan itself

**Rationale:** Code + docstrings + README = sufficient documentation

---

## 📖 WHERE TO FIND INFO?

| Need to know... | Look at... |
|-----------------|------------|
| Project overview | `/README.md` |
| How to setup agent | `/docs/QUICK_START.md` |
| File structure | `/docs/PROJECT_STRUCTURE.md` |
| What CIS rules | `/docs/selected_rules.md` |
| How `system_info.py` works | Read code + docstrings |
| How `http_client.py` works | Read code + docstrings |
| How auto-registration works | Read `agent/linux/main.py` + logs |

---

## 🎯 DOCUMENTATION PHILOSOPHY

**"Code is the documentation"**

- ✅ Self-documenting code with clear variable names
- ✅ Comprehensive docstrings in every function
- ✅ Type hints for clarity
- ✅ Inline comments for complex logic
- ✅ Logging for runtime behavior
- ❌ No separate explanation docs (duplicate effort)

**Keep docs:**
- Essential for users (QUICK_START)
- Essential for structure (PROJECT_STRUCTURE)
- Thesis requirements (scope.pdf, selected_rules.md)
- Future work (placeholders)

---

**🎉 Clean, focused, essential documentation only!**
