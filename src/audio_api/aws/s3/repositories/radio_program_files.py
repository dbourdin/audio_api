"""RadioProgramFilesRepository class."""

from audio_api.aws.s3.repositories import BaseS3Repository
from audio_api.aws.s3.schemas import RadioProgramFile, RadioProgramFileCreate


class RadioProgramFilesRepository(
    BaseS3Repository[RadioProgramFile, RadioProgramFileCreate]
):
    """RadioProgramFilesRepository class."""


radio_program_files_repository = RadioProgramFilesRepository(RadioProgramFile)
