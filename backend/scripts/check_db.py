"""
Script kiểm tra kết nối database và hiển thị thông tin version.

Usage:
    python scripts/check_db.py
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.database import engine, DATABASE_URL


def check_database():
    """Kiểm tra kết nối database."""
    print("🔍 Checking database connection...")
    print(f"📍 Database URL: {DATABASE_URL}")
    
    try:
        with engine.connect() as conn:
            # Kiểm tra version DB
            if "postgresql" in DATABASE_URL.lower():
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"✅ Connected to PostgreSQL")
                print(f"📦 Version: {version.split(',')[0]}")
            elif "sqlite" in DATABASE_URL.lower():
                result = conn.execute(text("SELECT sqlite_version();"))
                version = result.fetchone()[0]
                print(f"✅ Connected to SQLite")
                print(f"📦 Version: {version}")
            else:
                print(f"✅ Connected to database")
            
            # Kiểm tra tables
            if "postgresql" in DATABASE_URL.lower():
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public';"
                ))
            else:
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table';"
                ))
            
            table_count = result.fetchone()[0]
            print(f"📊 Tables in database: {table_count}")
            
            print("\n✅ Database check passed!")
            return True
            
    except Exception as e:
        print(f"\n❌ Database connection failed!")
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    success = check_database()
    exit(0 if success else 1)
