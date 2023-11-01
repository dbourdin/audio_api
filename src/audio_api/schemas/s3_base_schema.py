"""S3BaseSchema class."""

from pydantic import BaseModel


class S3BaseSchema(BaseModel):
    """S3BaseSchema class."""

    file_name: str | None
    file_url: str | None
