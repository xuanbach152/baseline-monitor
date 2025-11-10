"""Global dependencies for FastAPI."""
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # use db here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
