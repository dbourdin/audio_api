"""S3BaseModel Models."""
from typing import BinaryIO

from pydantic import BaseModel


class S3BaseModel(BaseModel):
    """S3BaseModel class."""

    file_name: str


class S3FileModel(S3BaseModel):
    """S3FileModel class."""

    file_url: str


class S3CreateModel(S3BaseModel):
    """S3CreateModel class."""

    file: BinaryIO
