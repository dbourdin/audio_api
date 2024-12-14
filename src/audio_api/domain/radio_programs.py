"""RadioPrograms interface to handle use cases."""
import uuid
from typing import BinaryIO

from audio_api.api.schemas import RadioProgramCreateInSchema, RadioProgramUpdateInSchema
from audio_api.aws.dynamodb.exceptions import DynamoDbClientError
from audio_api.aws.dynamodb.models import (
    RadioProgramPutItemModel,
    RadioProgramUpdateItemModel,
)
from audio_api.aws.dynamodb.repositories import radio_programs_repository
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.aws.s3.exceptions import S3ClientError, S3PersistenceError
from audio_api.aws.s3.models import RadioProgramFileCreate
from audio_api.aws.s3.repositories import radio_program_files_repository
from audio_api.aws.s3.repositories.radio_program_files import (
    RadioProgramFilesRepository,
)
from audio_api.domain.models import RadioProgramModel


class RadioPrograms:
    """RadioPrograms class used to create, read, update and delete radio programs."""

    radio_programs_repository: RadioProgramsRepository = radio_programs_repository
    radio_program_files_repository: RadioProgramFilesRepository = (
        radio_program_files_repository
    )

    @classmethod
    def _delete_file_from_s3(cls, file_name: str):
        """Delete file from S3 by file_name.

        Args:
            file_name: File to be deleted.
        """
        try:
            # Remove uploaded file in s3
            cls.radio_program_files_repository.delete_object(object_key=file_name)
        except (S3ClientError, S3PersistenceError):
            pass
            # TODO: Should we care if we failed to delete?
            # TODO: Run a monthly job to cleanup orphan programs?
            # This could potentially remove new uploaded programs during cleanup

    @classmethod
    def get(cls, *, program_id: uuid.UUID) -> RadioProgramModel:
        """Get a RadioProgram by program_id from DB.

        Args:
            program_id: program_id of the RadioProgram to retrieve.

        Returns:
            RadioProgramModel: Model containing stored data.
        """
        return cls.radio_programs_repository.get_item(item_id=program_id)

    @classmethod
    def get_all(cls) -> list[RadioProgramModel]:
        """Get all RadioPrograms from DB.

        Returns:
            list[RadioProgramModel]: List containing all stored RadioPrograms.
        """
        return cls.radio_programs_repository.get_items()

    @classmethod
    def create(
        cls,
        *,
        radio_program: RadioProgramCreateInSchema,
        program_file: BinaryIO,
    ) -> RadioProgramModel:
        """Create a new RadioProgram by uploading to s3 and storing metadata in DB.

        Args:
            radio_program: Input data.
            program_file: MP3 file containing the radio program.

        Raises:
            DynamoDbClientError: If failed to store new RadioProgram in DB.

        Returns:
            RadioProgramModel: Model containing stored data.
        """
        uploaded_file = cls.radio_program_files_repository.put_object(
            RadioProgramFileCreate(file_name=radio_program.title, file=program_file)
        )
        radio_program_db = RadioProgramPutItemModel(
            **radio_program.dict(), radio_program=uploaded_file
        )
        try:
            new_program = cls.radio_programs_repository.put_item(item=radio_program_db)
        except DynamoDbClientError as e:
            if uploaded_file.file_url:
                cls._delete_file_from_s3(file_name=uploaded_file.file_name)
            raise e

        return new_program

    @classmethod
    def update(
        cls,
        *,
        program_id: uuid.UUID,
        new_program: RadioProgramUpdateInSchema,
        program_file: BinaryIO = None,
    ) -> RadioProgramModel:
        """Update an existing RadioProgram with new properties and new file if included.

        Args:
            program_id: of the RadioProgram to retrieve.
            new_program: RadioProgramUpdateIn model with new data.
            program_file: If there is a program file, it will be uploaded to S3.

        Raises:
            DynamoDbClientError: If failed to update RadioProgram in DB.

        Returns:
            RadioProgramModel: Model containing updated data.
        """
        db_program = cls.get(program_id=program_id)
        existing_file = None
        if db_program.radio_program:
            existing_file = db_program.radio_program.file_name

        update_program = RadioProgramUpdateItemModel(**db_program.dict())
        update_program = update_program.copy(update=new_program.dict(exclude_none=True))

        if program_file:
            # Will throw RadioProgramS3Error if fails to persist program.
            uploaded_file = cls.radio_program_files_repository.put_object(
                RadioProgramFileCreate(
                    file_name=update_program.title, file=program_file
                )
            )
            update_program.radio_program = uploaded_file

        try:
            updated_program = radio_programs_repository.update_item(
                item_id=program_id, item=update_program
            )
        except DynamoDbClientError as e:
            if program_file:
                cls._delete_file_from_s3(
                    file_name=update_program.radio_program.file_name
                )

            raise e

        if program_file and db_program.radio_program:
            cls._delete_file_from_s3(file_name=existing_file)

        return updated_program

    @classmethod
    def delete(
        cls,
        *,
        program_id: uuid.UUID,
    ) -> None:
        """Remove an existing RadioProgram and S3 file if exists.

        Args:
            program_id: of the RadioProgram to be removed.
        """
        existing_program = cls.get(program_id=program_id)
        cls.radio_programs_repository.delete_item(item_id=program_id)
        if existing_program.radio_program:
            cls._delete_file_from_s3(file_name=existing_program.radio_program.file_name)
