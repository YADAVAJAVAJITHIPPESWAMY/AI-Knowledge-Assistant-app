"""
Database Session and Engine Management
Supports PostgreSQL with pgvector, and transparently falls back to SQLite for local development or unit testing.
"""
import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Determine database URL
db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
if os.getenv("TESTING", "0") == "1":
    db_url = settings.TEST_DATABASE_URL

# For SQLAlchemy 2.0 with psycopg v3, ensure dialect prefix is postgresql+psycopg
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

def _make_engine(url: str, args: dict):
    return create_engine(url, echo=False, connect_args=args, pool_pre_ping=True)

# Try the configured DB; if PostgreSQL is unavailable, fall back to SQLite automatically
engine = None
_using_sqlite_fallback = False

if not db_url.startswith("sqlite"):
    try:
        _test_engine = _make_engine(db_url, connect_args)
        with _test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = _test_engine
        print(f"[DB] Connected to: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    except Exception as e:
        _sqlite_url = "sqlite:///./local_dev.db"
        print(f"[DB] PostgreSQL not available ({e}). Falling back to SQLite: {_sqlite_url}")
        db_url = _sqlite_url
        connect_args = {"check_same_thread": False}
        _using_sqlite_fallback = True

if engine is None:
    engine = _make_engine(db_url, connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

