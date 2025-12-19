"""
Script xóa các bảng không sử dụng trong database.

Usage:
    python scripts/drop_unused_tables.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from sqlalchemy import text

TABLES_TO_DROP = [
    'activity_logs',
    'alerts',
    'anomaly_history',
    'api_tokens',
    'configurations',
    'reports',
    'schedules'
]


TABLES_TO_KEEP = [
    'users',
    'agents',
    'rules',
    'violations',
    'alembic_version'
]

def drop_unused_tables():
    """Xóa các bảng không sử dụng."""
    print("\n" + "="*60)
    print("DROP UNUSED TABLES")
    print("="*60)
    
    with engine.connect() as conn:
        # Kiểm tra các bảng hiện có
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        existing_tables = [row[0] for row in result.fetchall()]
        
        print("\nCurrent tables:")
        for table in existing_tables:
            status = "✓ KEEP" if table in TABLES_TO_KEEP else "✗ DROP"
            print(f"  {status}: {table}")
        
        # Xác nhận
        print("\n" + "-"*60)
        print(f"Will DROP {len(TABLES_TO_DROP)} tables:")
        for table in TABLES_TO_DROP:
            if table in existing_tables:
                print(f"  - {table}")
        
        response = input("\nProceed? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Cancelled.")
            return
        
        # Xóa từng bảng
        print("\n" + "-"*60)
        dropped_count = 0
        for table in TABLES_TO_DROP:
            if table in existing_tables:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                    conn.commit()
                    print(f"✓ Dropped: {table}")
                    dropped_count += 1
                except Exception as e:
                    print(f"✗ Failed to drop {table}: {e}")
        
        # Hiển thị kết quả
        print("\n" + "="*60)
        print(f"✓ Successfully dropped {dropped_count} tables")
        print("="*60)
        
        
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        remaining_tables = [row[0] for row in result.fetchall()]
        
        print("\nRemaining tables:")
        for table in remaining_tables:
            print(f"  ✓ {table}")
        print()

if __name__ == "__main__":
    drop_unused_tables()
