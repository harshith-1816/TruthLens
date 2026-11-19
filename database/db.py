"""
TruthLens - Database Configuration and PostgreSQL / SQLite Engine
Supports PostgreSQL with connection pooling and automated fallback to SQLite
for resilient, zero-configuration local execution and testing.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL from environment or default PostgreSQL connection string
# Fallback to local SQLite if PostgreSQL is unavailable
DEFAULT_PG_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/truthlens_db"
)

SQLITE_FALLBACK_URL = "sqlite:///./truthlens.db"

Base = declarative_base()

def get_engine():
    """Initializes database engine with PostgreSQL and graceful SQLite fallback."""
    db_url = DEFAULT_PG_URL
    try:
        # Check if Postgres driver can connect
        if db_url.startswith("postgresql"):
            engine = create_engine(db_url, pool_pre_ping=True, connect_args={"connect_timeout": 2})
            # Test connection
            with engine.connect() as conn:
                pass
            return engine, "postgresql"
    except Exception:
        pass
    
    # Graceful fallback to SQLite
    engine = create_engine(
        SQLITE_FALLBACK_URL,
        connect_args={"check_same_thread": False}
    )
    return engine, "sqlite"

engine, DB_DIALECT = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
