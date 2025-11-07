# AKBS Integration Plan
## Adding Knowledge Base Queries to Sensor System

**Status:** Ready to integrate  
**AKBS Location:** `~/aquaponics-knowledge-base-system`

---

## Quick Reference

**Fast Retrieval (Use This First):**
```python
from akbs_query import AKBSQuery

kb = AKBSQuery()
results = kb.query("What is optimal pH?")
# Returns in <1 second
```

**Slow LLM (Optional Future):**
```python
from akbs_query_with_llm import AKBSWithLLM

kb = AKBSWithLLM()
answer = kb.query_with_llm("Explain pH")
# Returns in ~30 seconds
```

---

## Integration Steps

### Step 1: Create AKBS Interface Module
File: `src/hydroponics/akbs/interface.py`

### Step 2: Add API Endpoints
File: `src/hydroponics/core/main.py`
- GET `/api/knowledge/query?q=...`
- POST `/api/knowledge/ask-ai` (optional)

### Step 3: Update Dashboard
File: `templates/dashboard.html`
- Add "More Info" buttons
- Display retrieved chunks
- Add "Ask AI" modal (optional)

---

## See Full Roadmap
`~/aquaponics-knowledge-base-system/INTEGRATION_ROADMAP.md`
