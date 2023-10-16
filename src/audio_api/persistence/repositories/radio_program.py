"""RadioProgramRepository to handle DB persistence."""

from uuid import UUID

from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from audio_api.persistence.models.radio_program import RadioProgram
from audio_api.persistence.repositories.base_repository import BaseRepository
from audio_api.schemas import RadioProgramCreateDB, RadioProgramUpdateDB


class RadioProgramDatabaseError(Exception):
    """RadioProgramDatabaseError class to handle DB errors."""


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

    def update(
        self,
        db: Session,
        *,
        db_program: RadioProgram,
        updated_program: RadioProgramUpdateDB,
    ) -> RadioProgram:
        """Update an existing RadioProgram.

        Args:
            db: A database session
            db_program: Existing RadioProgram in the DB.
            updated_program: Updated RadioProgram instance.

        Raises:
            RadioProgramDatabaseError: If failed to update RadioProgram.

        Returns:
            RadioProgram: The updated RadioProgram properties.
        """
        try:
            return super().update(db=db, db_obj=db_program, obj_in=updated_program)
        except DatabaseError as e:
            raise RadioProgramDatabaseError(
                f"Failed to update RadioProgram {db_program.program_id}: {e}"
            )


radio_programs_repository = RadioProgramRepository(RadioProgram)
