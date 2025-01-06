"""S3BaseModel Models."""
from tempfile import SpooledTemporaryFile
from typing import Any

from pydantic import BaseModel, field_validator
from slugify import slugify


class S3BaseModel(BaseModel):
    """S3BaseModel class."""

    file_name: str

    @field_validator("file_name", mode="before")
    def slugify_file_name(cls, value):
        """Slugify file_name to be URL friendly."""
        return slugify(value)


class S3FileModel(S3BaseModel):
    """S3FileModel class."""

    file_url: str


class S3CreateModel(S3BaseModel):
    """S3CreateModel class."""

    file: Any

    @field_validator("file")
    def validate_file(cls, value):
        """Validate that file is the required type."""
        if not isinstance(value, SpooledTemporaryFile):
            raise ValueError(
                f"File must be a SpooledTemporaryFile, got {type(value)} instead."
            )
        return value
