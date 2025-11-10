import subprocess
from scripts.seed_data import main as seed_main

def main():
    print("🔧 Setting up database...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    seed_main()
    print("🎉 Setup complete!")

if __name__ == "__main__":
    main()
