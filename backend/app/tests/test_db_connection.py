from sqlalchemy import text
from app.db.database import engine

def test_connection():
    try:
        with engine.connect() as conn:
            print("Connected:", conn.execute(text("SELECT version();")).fetchone())
    except Exception as e:
        print("Connection failed:", e)


if __name__ == "__main__":
    test_connection()