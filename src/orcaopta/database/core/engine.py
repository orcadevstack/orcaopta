import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# /app/data is guaranteed to exist and be writable
DB_DIR = "/app/data"
DB_PATH = os.path.join(DB_DIR, "orcaopta.db")

# Ensure directory exists
os.makedirs(DB_DIR, exist_ok=True)

# ---------------------------------------------------------
# Create SQLAlchemy engine
# ---------------------------------------------------------

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},  # required for SQLite + threads
    pool_pre_ping=True,                         # avoids stale connections
    pool_recycle=3600                           # long-running container safety
)

# ---------------------------------------------------------
# Session factory
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ---------------------------------------------------------
# Helper: get DB session
# ---------------------------------------------------------

def get_db():
    """FastAPI dependency / general DB accessor."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

