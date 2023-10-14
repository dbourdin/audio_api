"""Base database session file."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from audio_api.settings import get_settings

settings = get_settings()

# The database should already be created
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
