"""
Base ORM module for Orcaopta.
This file defines the shared SQLAlchemy Declarative Base that all ORM models must inherit from.
It ensures:
- Alembic can autogenerate migrations
- All models share the same metadata
- Database initialization works consistently
"""

from sqlalchemy.orm import declarative_base, declared_attr


class CustomBase:
    """
    A mixin that automatically generates __tablename__ from the class name
    unless explicitly defined.

    Example:
        class NodeState(Base):
            id = Column(Integer, primary_key=True)

        → __tablename__ becomes "node_state"
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


# Shared Base for ALL ORM models in Orcaopta
Base = declarative_base(cls=CustomBase)
