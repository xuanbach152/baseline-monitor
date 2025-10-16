baseline-monitor backend

This folder contains a minimal FastAPI backend for receiving agent reports.

Run locally (recommended in a virtualenv):

1. Install dependencies:

   pip install -r requirements.txt

2. Start server:

   uvicorn app.main:app --reload

The server exposes:
- POST /reports to submit an agent report
- GET /reports/latest/{agent_id} to fetch the latest report for an agent
