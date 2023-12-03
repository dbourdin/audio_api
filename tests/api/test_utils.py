"""Test util functions."""
import uuid
from pathlib import Path
from tempfile import SpooledTemporaryFile

from starlette.datastructures import Headers, UploadFile

from audio_api.domain.models import RadioProgramFileModel, RadioProgramModel

MAX_FILE_SIZE = 1024 * 1024


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


def create_upload_file(
    file: Path,
) -> tuple[UploadFile, bytes]:
    """Open a file and creates an UploadFile object.

    Args:
        file: File to upload.

    Returns:
        UploadFile: File to upload wrapped in UploadFile model.
        bytes: File content to be uploaded.
    """
    file_name = file.name
    headers = {
        "content-disposition": (
            f'form-data; name="program_file"; filename="{file_name}'
        ),
        # TODO: Extract from file?
        "content-type": "audio/mpeg",
    }
    headers = Headers(headers=headers)
    temp_file = SpooledTemporaryFile(max_size=MAX_FILE_SIZE)
    upload_file = UploadFile(
        file=temp_file, size=0, filename=file_name, headers=headers
    )
    with open(file, "rb") as f:
        file_content = f.read()
    upload_file.file.write(file_content)
    upload_file.file.seek(0)
    return upload_file, file_content
