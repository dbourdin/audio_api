"""RadioProgramFilesRepository class."""

from audio_api.aws.s3.models import RadioProgramFile, RadioProgramFileCreate
from audio_api.aws.s3.repositories import BaseS3Repository


class RadioProgramFilesRepository(
    BaseS3Repository[RadioProgramFile, RadioProgramFileCreate]
):
    """RadioProgramFilesRepository class."""


radio_program_files_repository = RadioProgramFilesRepository(RadioProgramFile)
