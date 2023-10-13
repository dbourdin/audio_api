"""API FastAPI dependencies."""

from collections.abc import Generator

from fastapi.security import OAuth2PasswordBearer

from audio_api.db.session import SessionLocal
from audio_api.settings import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


def get_db() -> Generator:
    """Get a db Session.

    Yields:
        Generator: A db Session as a generator
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
