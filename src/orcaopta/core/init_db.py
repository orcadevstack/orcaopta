from orcaopta.database.core.base import Base
from orcaopta.database.core.session import engine

def init_db():
    Base.metadata.create_all(bind=engine)
