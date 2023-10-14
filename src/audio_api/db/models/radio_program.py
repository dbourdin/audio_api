"""RadioProgram database table."""

from sqlalchemy import Column, Date, Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr

from audio_api.db.models.base_model import SqlAlchemyModel


class RadioProgram(SqlAlchemyModel):
    """RadioProgram database table."""

    program_id = Column(
        UUID(as_uuid=True),
        index=True,
        unique=True,
        server_default=text("uuid_generate_v4()"),
        nullable=False,
    )
    title = Column(String, nullable=False)
    description = Column(String)
    air_date = Column(Date)
    length = Column(Numeric)  # TODO: Consider convert to Int
    spotify_playlist = Column(String)
    url = Column(String)

    @declared_attr
    def __tablename__(cls) -> str:
        """Return the table name."""
        return "radio_programs"
