"""RadioPrograms interface to handle use cases."""
import uuid
from typing import BinaryIO

from audio_api import schemas
from audio_api.persistence.repositories import radio_programs_repository
from audio_api.persistence.repositories.radio_program import RadioProgramDatabaseError
from audio_api.s3.program_file_persistence import (
    ProgramFilePersistence,
    RadioProgramS3Error,
)
from audio_api.schemas.radio_program_dynamo import RadioProgram, RadioProgramCreateDB


class RadioPrograms:
    """RadioPrograms class used to create, read, update and delete radio programs."""

    repository = radio_programs_repository
    program_file_persistence = ProgramFilePersistence

    @classmethod
    def _delete_file_from_s3_by_url(cls, program_url: str):
        """Delete a program file from S3 from a given url.

        Args:
            program_url: URL of the file to be deleted.
        """
        try:
            # Remove uploaded file in s3
            cls.program_file_persistence.delete_program_by_url(url=program_url)
        except RadioProgramS3Error:
            pass
            # TODO: Should we care if we failed to delete?
            # TODO: Run a monthly job to cleanup orphan programs?
            # This could potentially remove new uploaded programs during cleanup

    @classmethod
    def _delete_file_from_s3(cls, file_name: str):
        """Delete file from S3 by file_name.

        Args:
            file_name: File to be deleted.
        """
        try:
            # Remove uploaded file in s3
            cls.program_file_persistence.delete_program(file_name=file_name)
        except RadioProgramS3Error:
            pass
            # TODO: Should we care if we failed to delete?
            # TODO: Run a monthly job to cleanup orphan programs?
            # This could potentially remove new uploaded programs during cleanup

    @classmethod
    def get(cls, *, program_id: uuid.UUID) -> RadioProgram:
        """Get a RadioProgram by program_id from DB.

        Args:
            program_id: program_id of the RadioProgram to retrieve.

        Returns:
            RadioProgram: Model containing stored data.
        """
        return cls.repository.get(program_id=program_id)

    @classmethod
    def get_all(cls) -> list[RadioProgram]:
        """Get all RadioPrograms from DB.

        Returns:
            list[RadioProgram]: List containing all stored RadioPrograms.
        """
        return cls.repository.get_all()

    @classmethod
    def create(
        cls,
        *,
        radio_program: schemas.RadioProgramCreateIn,
        program_file: BinaryIO,
    ) -> RadioProgram:
        """Create a new RadioProgram by uploading to s3 and storing metadata in DB.

        Args:
            radio_program: Input data.
            program_file: MP3 file containing the radio program.

        Raises:
            RadioProgramDatabaseError: If failed to store new RadioProgram in DB.

        Returns:
            RadioProgram: Model containing stored data.
        """
        uploaded_file = cls.program_file_persistence.persist_program(
            radio_program=radio_program, program_file=program_file
        )
        radio_program_db = RadioProgramCreateDB(
            **radio_program.dict(), program_file=uploaded_file
        )
        try:
            new_program = cls.repository.create(radio_program=radio_program_db)
        except RadioProgramDatabaseError as e:
            if uploaded_file.file_url:
                cls._delete_file_from_s3(file_name=uploaded_file.file_name)

            raise e

        return new_program

    @classmethod
    def update(
        cls,
        *,
        program_id: uuid.UUID,
        new_program: schemas.RadioProgramUpdateIn,
        program_file: BinaryIO = None,
    ) -> RadioProgram:
        """Update an existing RadioProgram with new properties and new file if included.

        Args:
            program_id: of the RadioProgram to retrieve.
            new_program: RadioProgramUpdateIn model with new data.
            program_file: If there is a program file, it will be uploaded to S3.

        Raises:
            RadioProgramDatabaseError: If failed to update RadioProgram in DB.

        Returns:
            RadioProgram: Model containing updated data.
        """
        db_program = cls.get(program_id=program_id)
        existing_file = None
        if db_program.radio_program:
            existing_file = db_program.radio_program.file_name

        update_program = schemas.RadioProgramUpdateDB(
            **db_program.dict(), **new_program.dict()
        )

        if program_file:
            # Will throw RadioProgramS3Error if fails to persist program.
            uploaded_file = cls.program_file_persistence.persist_program(
                radio_program=new_program, program_file=program_file
            )
            update_program.radio_program = uploaded_file

        try:
            updated_program = radio_programs_repository.update(
                program_id=program_id, updated_program=update_program
            )
        except RadioProgramDatabaseError as e:
            if program_file:
                cls._delete_file_from_s3(
                    file_name=update_program.radio_program.file_name
                )

            raise e

        if program_file and db_program.radio_program:
            cls._delete_file_from_s3(file_name=existing_file)

        return updated_program

    @classmethod
    def remove(
        cls,
        *,
        program_id: uuid.UUID,
    ) -> RadioProgram:
        """Remove an existing RadioProgram and S3 file if exists.

        Args:
            program_id: of the RadioProgram to be removed.

        Returns:
            RadioProgram: The removed RadioProgram.
        """
        existing_program = cls.repository.get(program_id=program_id)
        deleted_program = cls.repository.remove(program_id=program_id)
        if existing_program.url:
            cls._delete_file_from_s3(file_name=existing_program.radio_program.file_name)

        return deleted_program
