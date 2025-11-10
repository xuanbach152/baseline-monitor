"""
Script backup database ra file.

Usage:
    python scripts/backup_db.py
    python scripts/backup_db.py --output /path/to/backup.sql
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
import argparse
from datetime import datetime
from app.core.config import settings


def backup_database(output_path: str = None):
    """Backup database ra file SQL."""
    
    # Tạo tên file backup với timestamp
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        output_path = f"backups/backup_{timestamp}.sql"
    
    db_url = settings.DATABASE_URL
    
    print(f"🗄️  Starting database backup...")
    print(f"📁 Output file: {output_path}")
    
    try:
        if "postgresql" in db_url.lower():
            # Parse PostgreSQL URL
            # postgresql://user:pass@host:port/dbname
            # hoặc postgresql+psycopg2://user:pass@host:port/dbname
            
            # Bỏ protocol (postgresql:// hoặc postgresql+psycopg2://)
            url_without_protocol = db_url.split("://", 1)[1]
            
            # Split thành user:pass và host:port/dbname
            parts = url_without_protocol.split("@")
            user_pass = parts[0].split(":")
            host_db = parts[1].split("/")
            host_port = host_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "5433"
            dbname = host_db[1]
            
            # Run pg_dump
            cmd = [
                "pg_dump",
                "-h", host,
                "-p", port,
                "-U", user,
                "-d", dbname,
                "-f", output_path,
                "--clean",
                "--if-exists"
            ]
            
            env = {"PGPASSWORD": password}
            subprocess.run(cmd, env=env, check=True)
            
        elif "sqlite" in db_url.lower():
            # SQLite: just copy file
            db_path = db_url.replace("sqlite:///", "")
            import shutil
            shutil.copy2(db_path, output_path)
        
        else:
            print("❌ Unsupported database type")
            return False
        
        # Kiểm tra file size
        file_size = Path(output_path).stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        print(f"✅ Backup completed successfully!")
        print(f"📦 File size: {size_mb:.2f} MB")
        print(f"📍 Location: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Backup database")
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: backups/backup_TIMESTAMP.sql)"
    )
    args = parser.parse_args()
    
    success = backup_database(args.output)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
