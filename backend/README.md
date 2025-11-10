baseline-monitor backend

This folder contains a minimal FastAPI backend for receiving agent reports.

Run locally (recommended in a virtualenv):

# Tạo file migration mới (Alembic sẽ tự động phát hiện thay đổi trong models)
alembic revision --autogenerate -m "Tên mô tả migration"

# Áp dụng migration lên database
alembic upgrade head

source venv/bin/activate

1. Install dependencies:

   pip install -r requirements.txt

2. Start server:

   uvicorn app.main:app --reload

The server exposes:
- POST /reports to submit an agent report
- GET /reports/latest/{agent_id} to fetch the latest report for an agent

# 1. Kiểm tra container PostgreSQL đang chạy
docker ps

# 2. Truy cập vào container PostgreSQL
docker exec -it bach-db bash

# 3. Đăng nhập vào PostgreSQL
psql -U postgres -d compliance

# 4. Liệt kê các bảng hiện có
\dt

# (Tùy chọn) Xem bảng chứa thông tin version của Alembic
SELECT * FROM alembic_version;

# 5. Thoát khỏi psql và container
\q
exit
