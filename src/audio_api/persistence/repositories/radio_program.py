"""RadioProgramRepository to handle DB persistence."""

from uuid import UUID

from sqlalchemy.orm import Session

from audio_api.persistence.models.radio_program import RadioProgram
from audio_api.persistence.repositories.base_repository import BaseRepository
from audio_api.schemas import RadioProgramCreateDB, RadioProgramUpdateDB


class RadioProgramRepository(
    BaseRepository[RadioProgram, RadioProgramCreateDB, RadioProgramUpdateDB]
):
    """RadioProgramRepository to handle DB persistence."""

    def get_by_program_id(self, db: Session, program_id: UUID) -> RadioProgram | None:
        """Get a single radio program by program_id.

        Args:
            db (Session): A database session
            program_id (UUID): The program_id to retrieve

        Returns:
            Optional[RadioProgram]: The retrieved radio program
        """
        return db.query(self.model).filter(self.model.program_id == program_id).first()


radio_programs_repository = RadioProgramRepository(RadioProgram)
