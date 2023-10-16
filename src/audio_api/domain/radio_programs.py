"""RadioPrograms interface to handle use cases."""
import uuid
from typing import BinaryIO

from sqlalchemy.orm import Session

from audio_api import schemas
from audio_api.persistence.models import RadioProgram
from audio_api.persistence.repositories import radio_programs_repository
from audio_api.s3.program_file_persistence import ProgramFilePersistence
from audio_api.schemas import RadioProgramCreateDB


class RadioPrograms:
    """RadioPrograms class used to create, read, update and delete radio programs."""

    repository = radio_programs_repository
    program_file_persistence = ProgramFilePersistence

    @classmethod
    def get(
        cls,
        *,
        db: Session,
        program_id: uuid.UUID,
    ) -> RadioProgram:
        """Get a RadioProgram by program_id from DB.

        Args:
            db (Session): A database session.
            program_id: program_id of the RadioProgram to retrieve.

        Returns:
            RadioProgram: Model containing stored data.
        """
        return cls.repository.get_by_program_id(db=db, program_id=program_id)

    @classmethod
    def get_all(
        cls,
        *,
        db: Session,
    ) -> list[RadioProgram]:
        """Get all RadioPrograms from DB.

        Args:
            db (Session): A database session.

        Returns:
            list[RadioProgram]: List containing all stored RadioPrograms.
        """
        return cls.repository.get_multi(db=db)

    @classmethod
    def create(
        cls,
        *,
        db: Session,
        radio_program: schemas.RadioProgramCreateIn,
        program_file: BinaryIO,
    ) -> RadioProgram:
        """Create a new RadioProgram by uploading to s3 and storing metadata in DB.

        Args:
            db (Session): A database session.
            radio_program: Input data.
            program_file: MP3 file containing the radio program.

        Returns:
            RadioProgram: Model containing stored data.
        """
        url = cls.program_file_persistence.persist_program(
            radio_program=radio_program, program_file=program_file
        )
        # TODO: Delete element from S3 if failed to store on DB.
        # TODO: Extract audio length
        radio_program_db = RadioProgramCreateDB(**radio_program.dict(), url=url)
        return cls.repository.create(db, obj_in=radio_program_db)
