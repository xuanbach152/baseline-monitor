"""
Script dọn dẹp logs cũ và dữ liệu tạm.

Usage:
    python scripts/clean_old_logs.py
    python scripts/clean_old_logs.py --days 30
    python scripts/clean_old_logs.py --dry-run
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from datetime import datetime, timedelta
from sqlalchemy import text
from app.db.database import SessionLocal


def clean_log_files(days: int, dry_run: bool = False):
    """Xóa log files cũ hơn N ngày."""
    print(f"🧹 Cleaning log files older than {days} days...")
    
    log_dirs = [
        Path("logs"),
        Path("app/logs"),
        Path("/var/log/baseline-monitor")
    ]
    
    cutoff_date = datetime.now() - timedelta(days=days)
    total_deleted = 0
    total_size = 0
    
    for log_dir in log_dirs:
        if not log_dir.exists():
            continue
        
        for log_file in log_dir.glob("**/*.log*"):
            if log_file.is_file():
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    file_size = log_file.stat().st_size
                    
                    if dry_run:
                        print(f"  [DRY-RUN] Would delete: {log_file} ({file_size} bytes)")
                    else:
                        log_file.unlink()
                        print(f"  ✅ Deleted: {log_file}")
                    
                    total_deleted += 1
                    total_size += file_size
    
    size_mb = total_size / (1024 * 1024)
    action = "Would free" if dry_run else "Freed"
    print(f"✅ {action} {size_mb:.2f} MB by deleting {total_deleted} log files")


def clean_old_reports(days: int, dry_run: bool = False):
    """Xóa reports cũ trong database."""
    print(f"\n🧹 Cleaning reports older than {days} days...")
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Count old reports
        count_query = text("""
            SELECT COUNT(*) FROM agent_reports 
            WHERE created_at < :cutoff_date
        """)
        result = db.execute(count_query, {"cutoff_date": cutoff_date})
        count = result.scalar()
        
        if count == 0:
            print("  ℹ️  No old reports to delete")
            return
        
        if dry_run:
            print(f"  [DRY-RUN] Would delete {count} old reports")
        else:
            # Delete old reports
            delete_query = text("""
                DELETE FROM agent_reports 
                WHERE created_at < :cutoff_date
            """)
            db.execute(delete_query, {"cutoff_date": cutoff_date})
            db.commit()
            print(f"  ✅ Deleted {count} old reports")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def clean_temp_files(dry_run: bool = False):
    """Xóa temporary files."""
    print(f"\n🧹 Cleaning temporary files...")
    
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "__pycache__",
        "*.pyc",
        ".pytest_cache"
    ]
    
    total_deleted = 0
    
    for pattern in temp_patterns:
        for temp_file in Path(".").rglob(pattern):
            if temp_file.is_file():
                if dry_run:
                    print(f"  [DRY-RUN] Would delete: {temp_file}")
                else:
                    temp_file.unlink()
                    print(f"  ✅ Deleted: {temp_file}")
                total_deleted += 1
            elif temp_file.is_dir():
                if dry_run:
                    print(f"  [DRY-RUN] Would delete dir: {temp_file}")
                else:
                    import shutil
                    shutil.rmtree(temp_file)
                    print(f"  ✅ Deleted dir: {temp_file}")
                total_deleted += 1
    
    print(f"✅ Cleaned {total_deleted} temporary items")


def main():
    parser = argparse.ArgumentParser(description="Clean old logs and data")
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="Delete files older than N days (default: 30)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--logs-only",
        action="store_true",
        help="Only clean log files"
    )
    parser.add_argument(
        "--reports-only",
        action="store_true",
        help="Only clean old reports"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("🧹 CLEANUP SCRIPT")
    print("="*60)
    
    if args.dry_run:
        print("⚠️  DRY-RUN MODE: Nothing will be deleted")
    
    if args.logs_only:
        clean_log_files(args.days, args.dry_run)
    elif args.reports_only:
        clean_old_reports(args.days, args.dry_run)
    else:
        clean_log_files(args.days, args.dry_run)
        clean_old_reports(args.days, args.dry_run)
        clean_temp_files(args.dry_run)
    
    print("\n" + "="*60)
    print("✅ Cleanup completed!")
    print("="*60)


if __name__ == "__main__":
    main()
