"""Test util functions."""
import uuid
from tempfile import SpooledTemporaryFile

from audio_api.domain.models import RadioProgramFileModel, RadioProgramModel


def radio_program(title: str) -> RadioProgramModel:
    """Return a RadioProgramModel for testing."""
    return RadioProgramModel(
        id=uuid.uuid4(),
        title=title,
        radio_program=RadioProgramFileModel(
            file_name="test_file",
            file_url="test_file",
        ),
    )


def create_temp_file() -> dict:
    """Return a dict containing a SpooledTemporaryFile prepared for form-data."""
    return {
        "program_file": ("program_file", SpooledTemporaryFile(), "multipart/form-data")
    }
