"""S3BaseModel Models."""
from tempfile import SpooledTemporaryFile
from typing import Any

from pydantic import BaseModel, validator


class S3BaseModel(BaseModel):
    """S3BaseModel class."""

    file_name: str


class S3FileModel(S3BaseModel):
    """S3FileModel class."""

    file_url: str


class S3CreateModel(S3BaseModel):
    """S3CreateModel class."""

    file: Any

    @validator("file")
    def validate_file(cls, value):
        """Validate that file is the required type."""
        if not isinstance(value, SpooledTemporaryFile):
            raise ValueError(
                f"File must be a SpooledTemporaryFile, got {type(value)} instead."
            )
        return value
