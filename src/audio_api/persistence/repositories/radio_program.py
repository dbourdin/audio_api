"""RadioProgramRepository to handle DB persistence."""

from uuid import UUID

from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import Session

from audio_api.persistence.models.radio_program import RadioProgram
from audio_api.persistence.repositories.base_repository import BaseRepository
from audio_api.schemas import RadioProgramCreateDB, RadioProgramUpdateDB


class RadioProgramDatabaseError(Exception):
    """RadioProgramDatabaseError class to handle DB errors."""


class RadioProgramNotFoundError(Exception):
    """RadioProgramNotFoundError class."""


class RadioProgramAlreadyExistsError(Exception):
    """RadioProgramAlreadyExistsError class."""


class RadioProgramRepository(
    BaseRepository[RadioProgram, RadioProgramCreateDB, RadioProgramUpdateDB]
):
    """RadioProgramRepository to handle DB persistence."""

    def get_by_program_id(self, db: Session, program_id: UUID) -> RadioProgram:
        """Get a RadioProgram program by program_id.

        Args:
            db (Session): A database session
            program_id (UUID): The program_id to retrieve

        Raises:
            RadioProgramNotFoundError: If the program is not found

        Returns:
            RadioProgram: The retrieved radio program
        """
        db_program = (
            db.query(self.model).filter(self.model.program_id == program_id).first()
        )
        if db_program is None:
            raise RadioProgramNotFoundError(
                f"Couldn't find RadioProgram with id: {program_id}"
            )

        return db_program

    def create(
        self, db: Session, *, radio_program: RadioProgramCreateDB
    ) -> RadioProgram:
        """Create a new RadioProgram.

        Args:
            db: A database session
            radio_program: RadioProgram to be created.

        Raises:
            RadioProgramAlreadyExistsError: If failed to create a new RadioProgram.
            RadioProgramDatabaseError: If failed to store new RadioProgram.

        Returns:
            RadioProgram: The created RadioProgram.
        """
        try:
            return super().create(db=db, obj_in=radio_program)
        except IntegrityError as e:
            raise RadioProgramAlreadyExistsError(
                f"Failed to create new RadioProgram: {e}"
            )
        except DatabaseError as e:
            raise RadioProgramDatabaseError(f"Failed to create new RadioProgram: {e}")

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

    def remove(self, db: Session, *, id: int) -> RadioProgram:
        """Remove an existing RadioProgram from the DB.

        Args:
            db: A database session
            id: ID of the RadioProgram to be removed.

        Raises:
            RadioProgramDatabaseError: If failed to remove existing RadioProgram.

        Returns:
            RadioProgram: The removed RadioProgram.
        """
        try:
            return super().remove(db=db, id=id)
        except DatabaseError as e:
            raise RadioProgramDatabaseError(
                f"Failed to remove existing RadioProgram: {e}"
            )


radio_programs_repository = RadioProgramRepository(RadioProgram)
