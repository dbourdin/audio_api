"""RadioProgramRepository to handle DB persistence."""

from audio_api.db.models.radio_program import RadioProgram
from audio_api.db.repositories.base_repository import BaseRepository
from audio_api.schemas import RadioProgramCreateDB, RadioProgramUpdateDB


class RadioProgramRepository(
    BaseRepository[RadioProgram, RadioProgramCreateDB, RadioProgramUpdateDB]
):
    """RadioProgramRepository to handle DB persistence."""


radio_program_repository = RadioProgramRepository(RadioProgram)
