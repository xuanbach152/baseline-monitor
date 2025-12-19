"""
Script reset database (drop all tables, recreate, migrate, seed).
CHỈ DÙNG TRONG MÔI TRƯỜNG DEV - SẼ XÓA TOÀN BỘ DỮ LIỆU!

Usage:
    python scripts/reset_db.py --force
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
import argparse
from sqlalchemy import text
from app.db.database import engine, Base, SessionLocal
from app.core.config import settings


def confirm_reset():
    """Xác nhận trước khi reset."""
    print("\n" + "="*60)
    print("WARNING: DATABASE RESET")
    print("="*60)
    print(f"Database: {settings.DATABASE_URL}")
    print("\nThis will:")
    print("  1. DROP all tables")
    print("  2. Recreate tables")
    print("  3. Run migrations")
    print("  4. Seed sample data")
    print("\nALL DATA WILL BE LOST!")
    print("="*60)
    
    response = input("\nType 'RESET' to confirm: ")
    return response == "RESET"


def drop_all_tables():
    """Drop toàn bộ tables và reset Alembic history."""
    print("\n Dropping all tables and resetting Alembic...")
    
    try:
        with engine.connect() as conn:
            # Drop all tables in public schema (PostgreSQL specific)
            print("  - Dropping all tables in public schema...")
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result]
            
            for table in tables:
                print(f"    Dropping table: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            
            # Commit transaction
            conn.commit()
        
        print("All tables dropped successfully")
        return True
    except Exception as e:
        print(f"Error dropping tables: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_tables():
    """Tạo lại tables - SKIPPED (Alembic migrations sẽ làm việc này)."""
    print("\nSkipping manual table creation (using Alembic migrations)...")
    # Không cần tạo tables manually vì Alembic sẽ tạo
    # Base.metadata.create_all(bind=engine)
    print(" Ready for migrations")
    return True


def run_migrations():
    """Chạy Alembic migrations."""
    print("\n Running Alembic migrations...")
    
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print(" Migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Migration failed: {e}")
        return False


def seed_data():
    """Seed dữ liệu mẫu."""
    print("\n Seeding sample data...")
    
    try:
        from scripts.seed_data import main as seed_main
        seed_main()
        return True
    except Exception as e:
        print(f" Seeding failed: {e}")
        return False


def reset_database(force: bool = False):
    """Reset toàn bộ database."""
    
    # Kiểm tra môi trường
    env = settings.ENV if hasattr(settings, 'ENV') else "development"
    if env == "production" and not force:
        print("Cannot reset production database without --force flag!")
        return False
    
    # Xác nhận
    if not force and not confirm_reset():
        print("\n Reset cancelled.")
        return False
    
    print("\n Starting database reset...")
    
    # Execute reset steps
    steps = [
        ("Drop tables", drop_all_tables),
        ("Create tables", create_tables),
        ("Run migrations", run_migrations),
        ("Seed data", seed_data),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n Reset failed at step: {step_name}")
            return False
    
    print("\n" + "="*60)
    print(" Database reset completed successfully!")
    print("="*60)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Reset database (DEV ONLY)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/reset_db.py --force
  python scripts/reset_db.py --force --yes
        """
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reset without confirmation (required)"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )
    
    args = parser.parse_args()
    
    if not args.force:
        print(" Error: --force flag is required for safety")
        print("Usage: python scripts/reset_db.py --force")
        sys.exit(1)
    
    success = reset_database(force=args.yes)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
