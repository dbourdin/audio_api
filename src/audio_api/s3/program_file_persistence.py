"""ProgramFilePersistence class to persist RadioPrograms in S3."""

import datetime
from typing import BinaryIO

from botocore.response import StreamingBody

from audio_api.s3.s3_connector import S3Connector
from audio_api.schemas import RadioProgramCreateIn
from audio_api.settings import get_settings

settings = get_settings()


class ProgramFilePersistence:
    """Class used to persist RadioPrograms in RADIO_PROGRAMS_BUCKET."""

    s3_connector = S3Connector(bucket_name=settings.RADIO_PROGRAMS_BUCKET)

    @classmethod
    def persist_program(
        cls, radio_program: RadioProgramCreateIn, program_file: BinaryIO
    ) -> str:
        """Persist a RadioProgram in RADIO_PROGRAMS_BUCKET.

        Args:
            radio_program: RadioProgram instance.
            program_file: RadioProgram file to be stored.

        Returns:
            str: url containing the persisted file.
        """
        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{timestamp}_{radio_program.title}.mp3"
        return cls.s3_connector.store(object_key=file_name, object_data=program_file)

    @classmethod
    def read_program(cls, file_name: str) -> StreamingBody:
        """Read an object persisted in RADIO_PROGRAMS_BUCKET by file_name.

        Args:
            file_name: File to be read.

        Returns:
            StreamingBody: Persisted object in RADIO_PROGRAMS_BUCKET.
        """
        return cls.s3_connector.read_object(object_key=file_name)

    @classmethod
    def delete_program(cls, file_name: str):
        """Delete an object persisted in RADIO_PROGRAMS_BUCKET by file_name.

        Args:
            file_name: File to be deleted.
        """
        cls.s3_connector.delete_object(object_key=file_name)
