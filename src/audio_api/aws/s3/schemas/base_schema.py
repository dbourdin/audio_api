"""S3BaseSchema class."""
from typing import BinaryIO

from pydantic import BaseModel


class S3BaseSchema(BaseModel):
    """S3BaseSchema class."""

    file_name: str


class S3FileSchema(S3BaseSchema):
    """S3FileSchema class."""

    file_url: str


class S3CreateSchema(S3BaseSchema):
    """S3CreateSchema class."""

    file: BinaryIO
