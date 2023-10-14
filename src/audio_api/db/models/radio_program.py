"""RadioProgram database table."""

from sqlalchemy import Column, Date, Numeric, String

from audio_api.db.base_class import Base


class RadioProgram(Base):
    """RadioProgram database table."""

    title = Column(String, nullable=False)
    description = Column(String)
    air_date = Column(Date)
    length = Column(Numeric)  # TODO: Consider convert to Int
    spotify_playlist = Column(String)
    url = Column(String)
