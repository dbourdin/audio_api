"""SQLAlchemy base class."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.sql.functions import now


@as_declarative()
class Base:
    """SQLAlchemy base class."""

    __name__: str
    # Generate __tablename__ automatically

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(
        UUID(as_uuid=True),
        index=True,
        unique=True,
        server_default=text("uuid_generate_v4()"),
    )

    created_at = Column(DateTime(timezone=True), server_default=now())
    updated_at = Column(
        DateTime(timezone=True), server_default=now(), onupdate=datetime.now
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Return the table name."""
        return cls.__name__.lower()
