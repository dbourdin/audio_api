"""Program Schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from audio_api.schemas import APISchema


class BaseProgramSchema(APISchema):
    """Base Program API Model."""

    title: str | None = Field(example="Shopping 2.0 #1")


class ProgramCreateIn(BaseProgramSchema):
    """Parameters received in a POST request."""


class ProgramCreateDB(ProgramCreateIn):
    """Model used to create a new record in a POST request."""


class ProgramCreateOut(BaseProgramSchema):
    """Parameters returned in a POST request."""

    uuid: UUID
    created_at: datetime
    updated_at: datetime


class ProgramGet(ProgramCreateOut):
    """Parameters returned in a GET request."""


class ProgramList(ProgramGet):
    """Parameters returned in a GET LIST request."""


class ProgramUpdateIn(BaseProgramSchema):
    """Parameters received in a PUT request."""


class ProgramUpdateDB(ProgramUpdateIn):
    """Model used to update a record in a PUT request."""


class ProgramUpdateOut(ProgramCreateOut):
    """Parameters returned in a PUT request."""
