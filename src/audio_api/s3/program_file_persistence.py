"""ProgramFilePersistence class to persist RadioPrograms in S3."""

import datetime
from typing import BinaryIO

from botocore.response import StreamingBody

from audio_api.s3.s3_connector import S3ClientError, S3Connector, S3PersistenceError
from audio_api.schemas import RadioProgramCreateIn, RadioProgramFileSchema
from audio_api.settings import get_settings

settings = get_settings()


class RadioProgramS3Error(Exception):
    """RadioProgramS3Error class to handle S3 errors."""


class ProgramFilePersistence:
    """Class used to persist RadioPrograms in RADIO_PROGRAMS_BUCKET."""

    s3_connector = S3Connector(bucket_name=settings.RADIO_PROGRAMS_BUCKET)

    @classmethod
    def persist_program(
        cls, radio_program: RadioProgramCreateIn, program_file: BinaryIO
    ) -> RadioProgramFileSchema:
        """Persist a RadioProgram in RADIO_PROGRAMS_BUCKET.

        Args:
            radio_program: RadioProgram instance.
            program_file: RadioProgram file to be stored.

        Raises:
            RadioProgramS3Error: If failed to store file on RADIO_PROGRAMS_BUCKET.

        Returns:
            RadioProgramFileSchema: Model containing the uploaded file metadata.
        """
        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{timestamp}_{radio_program.title}.mp3"
        try:
            s3_file = cls.s3_connector.store(
                object_key=file_name, object_data=program_file
            )
        except (S3ClientError, S3PersistenceError) as e:
            raise RadioProgramS3Error(f"Failed to store new RadioProgram on S3: {e}")

        # TODO: Extract audio length
        return RadioProgramFileSchema(**s3_file.dict(), length=0)

    @classmethod
    def read_program(cls, file_name: str) -> StreamingBody:
        """Read a RadioProgram from RADIO_PROGRAMS_BUCKET by file_name.

        Args:
            file_name: File to be read.

        Returns:
            StreamingBody: Persisted object in RADIO_PROGRAMS_BUCKET.
        """
        return cls.s3_connector.read_object(object_key=file_name)

    @classmethod
    def delete_program(cls, file_name: str):
        """Delete a RadioProgram in RADIO_PROGRAMS_BUCKET by file_name.

        Args:
            file_name: File to be deleted.

        Raises:
            RadioProgramS3Error: If failed to remove file from S3.
        """
        try:
            cls.s3_connector.delete_object(object_key=file_name)
        except (S3ClientError, S3PersistenceError) as e:
            raise RadioProgramS3Error(
                f"Failed to delete {file_name} RadioProgram file from S3: {e}"
            )

    # TODO: Store file_name in metadata and remove this method
    @classmethod
    def delete_program_by_url(cls, url: str):
        """Delete a RadioProgram in RADIO_PROGRAMS_BUCKET by url.

        Args:
            url: URL to the file to be deleted.
        """
        file_name = url.split("/")[-1]
        cls.delete_program(file_name=file_name)

    @classmethod
    def read_all(cls) -> list[str]:
        """Get a list with all RadioPrograms created in RADIO_PROGRAMS_BUCKET.

        Returns:
            list[str]: List containing all files in RADIO_PROGRAMS_BUCKET.
        """
        return cls.s3_connector.list_all()
