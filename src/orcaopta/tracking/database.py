from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

def get_engine(uri="sqlite:///orcaopta.db"):
    return create_engine(uri, echo=False, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False)
