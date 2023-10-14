"""RadioProgram database table."""

from sqlalchemy import Column, Numeric, String

from audio_api.db.base_class import Base


class RadioProgram(Base):
    """RadioProgram database table."""

    title = Column(String, nullable=False)
    description = Column(String)
    length = Column(Numeric)  # TODO: Consider convert to Int
    spotify_playlist = Column(String)
    url = Column(String)
