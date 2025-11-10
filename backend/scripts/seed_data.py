"""
Script seed dữ liệu mẫu vào database.

Usage:
    python scripts/seed_data.py
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.models.user import User
from app.models.rule import Rule
from app.models.agent import Agent
from app.models.violation import Violation
from app.models.alert import Alert
from app.models.schedule import Schedule
from passlib.context import CryptContext
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_users(db: Session):
    """Seed multiple users với các roles khác nhau."""
    print("🧑‍💼 Seeding users...")
    
    users_data = [
        {"username": "admin", "email": "admin@baseline.local", 
         "password": "admin123", "role": "admin", "is_active": True},
        {"username": "operator", "email": "operator@baseline.local", 
         "password": "operator123", "role": "operator", "is_active": True},
        {"username": "viewer", "email": "viewer@baseline.local", 
         "password": "viewer123", "role": "viewer", "is_active": True},
    ]
    
    created_count = 0
    for user_data in users_data:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            db.add(User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=pwd_context.hash(user_data["password"]),
                role=user_data["role"],
                is_active=user_data["is_active"]
            ))
            created_count += 1
            print(f"  ✓ Created user: {user_data['username']} (role: {user_data['role']})")
    
    if created_count > 0:
        db.commit()
        print(f"✅ Created {created_count} new users.")
    else:
        print("  - All users already exist.")


def seed_rules(db: Session):
    """Seed CIS Benchmark rules."""
    if db.query(Rule).count() > 0:
        print("✅ Rules already exist.")
        return

    print("📋 Inserting CIS benchmark rules...")
    
    rules = [
        Rule(
            name="Ensure SSH root login is disabled",
            description="Prevent direct root login via SSH",
            check_expression="sshd -T | grep -i 'permitrootlogin no'",
            severity="high",
            active=True
        ),
        Rule(
            name="Ensure SSH PermitEmptyPasswords is disabled",
            description="Disallow empty passwords",
            check_expression="sshd -T | grep -i 'permitemptypasswords no'",
            severity="high",
            active=True
        ),
        Rule(
            name="Ensure ufw service is enabled",
            description="Enable ufw service at boot",
            check_expression="systemctl is-enabled ufw",
            severity="high",
            active=True
        ),
    ]
    
    db.add_all(rules)
    db.commit()
    print(f"✅ Seeded {len(rules)} CIS rules successfully.")


def seed_agents(db: Session):
    """Seed sample agents."""
    if db.query(Agent).count() > 0:
        print("✅ Agents already exist.")
        return

    print("🖥️  Seeding sample agents...")
    
    agents = [
        Agent(
            hostname="web-server-01",
            ip_address="192.168.1.10",
            os="Ubuntu 22.04 LTS",
            version="1.0.0",
            is_online=True,
            last_checkin=datetime.now()
        ),
        Agent(
            hostname="db-server-01",
            ip_address="192.168.1.11",
            os="Ubuntu 20.04 LTS",
            version="1.0.0",
            is_online=True,
            last_checkin=datetime.now() - timedelta(minutes=5)
        ),
    ]
    
    db.add_all(agents)
    db.commit()
    print(f"✅ Seeded {len(agents)} agents successfully.")


def main():
    db = SessionLocal()
    try:
        print("\n" + "="*60)
        print("🌱 Starting database seeding...")
        print("="*60 + "\n")
        
        seed_users(db)
        print()
        seed_rules(db)
        print()
        seed_agents(db)
        
        print("\n" + "="*60)
        print("✅ All seed data completed successfully!")
        print("="*60)
        print("\n📝 Default credentials:")
        print("  Admin:    username=admin    password=admin123")
        print("  Operator: username=operator password=operator123")
        print("  Viewer:   username=viewer   password=viewer123")
        print()
    finally:
        db.close()


if __name__ == "__main__":
    main()
