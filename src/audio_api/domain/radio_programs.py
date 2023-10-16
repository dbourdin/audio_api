"""RadioPrograms interface to handle use cases."""
import uuid
from typing import BinaryIO

from sqlalchemy.orm import Session

from audio_api import schemas
from audio_api.persistence.models import RadioProgram
from audio_api.persistence.repositories import radio_programs_repository
from audio_api.persistence.repositories.radio_program import RadioProgramDatabaseError
from audio_api.s3.program_file_persistence import (
    ProgramFilePersistence,
    RadioProgramS3Error,
)
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

    @classmethod
    def update(
        cls,
        *,
        db: Session,
        program_id: uuid.UUID,
        new_program: schemas.RadioProgramUpdateIn,
        program_file: BinaryIO = None,
    ) -> RadioProgram:
        """Update an existing RadioProgram with new properties and new file if included.

        Args:
            db: A database session.
            program_id: of the RadioProgram to retrieve.
            new_program: RadioProgramUpdateIn model with new data.
            program_file: If there is a program file, it will be uploaded to S3.

        Raises:
            RadioProgramDatabaseError: If failed to update RadioProgram in DB.

        Returns:
            RadioProgram: Model containing updated data.
        """
        db_program = cls.get(db=db, program_id=program_id)
        update_program = schemas.RadioProgramUpdateDB(**new_program.dict())

        if program_file:
            # Will throw RadioProgramS3Error if fails to persist program.
            url = cls.program_file_persistence.persist_program(
                radio_program=new_program, program_file=program_file
            )
            update_program.url = url

        try:
            updated_program = radio_programs_repository.update(
                db=db, db_obj=db_program, obj_in=update_program
            )
        except RadioProgramDatabaseError as e:
            if update_program.url:
                try:
                    # Remove uploaded file in s3
                    cls.program_file_persistence.delete_program_by_url(
                        update_program.url
                    )
                except RadioProgramS3Error:
                    pass
                    # TODO: Should we care if we failed to delete?
                    # TODO: Run a monthly job to cleanup orphan programs?
                    # This could potentially remove new uploaded programs during cleanup
            raise e

        if updated_program.url and db_program.url:
            try:
                # Remove previous file in s3
                cls.program_file_persistence.delete_program_by_url(db_program.url)
            except RadioProgramS3Error:
                pass
                # TODO: Should we care if we failed to delete?
                # TODO: Run a monthly job to cleanup orphan programs?
                # This could potentially remove new uploaded programs during cleanup

        return updated_program
