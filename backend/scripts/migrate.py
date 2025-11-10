import subprocess

def run_migrations():
    print("🚀 Running Alembic migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("✅ Migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()
