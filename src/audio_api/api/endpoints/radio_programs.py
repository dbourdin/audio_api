"""Endpoints related to Radio Programs."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from audio_api.api.schemas import (
    APIMessage,
    RadioProgramCreateInSchema,
    RadioProgramCreateOutSchema,
    RadioProgramGetSchema,
    RadioProgramListSchema,
    RadioProgramUpdateInSchema,
    RadioProgramUpdateOutSchema,
)
from audio_api.api.schemas.utils import as_form
from audio_api.aws.dynamodb.exceptions import (
    DynamoDbClientError,
    DynamoDbItemNotFoundError,
    DynamoDbStatusError,
)
from audio_api.aws.s3.exceptions import S3ClientError, S3PersistenceError
from audio_api.domain.radio_programs import RadioPrograms

router = APIRouter()


@router.get(
    "/{program_id}",
    response_model=RadioProgramGetSchema,
    summary="Retrieve a single RadioProgram by UUID",
    description="Retrieve single a RadioProgram by UUID",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": APIMessage},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIMessage},
    },
)
async def get(
    *,
    program_id: uuid.UUID,
) -> Any:
    """Retrieve an existing Program.

    Args:
        program_id: The UUID of the RadioProgram to retrieve.

    Raises:
        HTTPException: HTTP_404_NOT_FOUND
            If RadioProgram does not exist.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to retrieve RadioProgram from the DB.
    """
    try:
        return RadioPrograms.get(program_id=program_id)
    except DynamoDbItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadioProgram not found.",
        )
    except (DynamoDbClientError, DynamoDbStatusError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve RadioProgram from the DB.",
        )


@router.get(
    "",
    response_model=list[RadioProgramListSchema],
    summary="List RadioPrograms",
    description="Get a list of RadioPrograms",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIMessage},
    },
)
def get_all() -> Any:
    """Retrieve all RadioProgram.

    Raises:
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to retrieve RadioPrograms.
    """
    try:
        return RadioPrograms.get_all()
    except (DynamoDbClientError, DynamoDbStatusError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve RadioPrograms from the DB.",
        )


@router.post(
    "",
    response_model=RadioProgramCreateOutSchema,
    summary="Create a RadioProgram",
    description="Create a RadioProgram",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": APIMessage},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIMessage},
    },
)
async def create(
    *,
    program_in: RadioProgramCreateInSchema = Depends(
        as_form(RadioProgramCreateInSchema)
    ),
    program_file: UploadFile = File(...),
) -> Any:
    """Create a new RadioProgram.

    Args:
        program_in: New RadioProgram.
        program_file: RadioProgram MP3 file.

    Raises:
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to store RadioProgram on DB.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to connect to S3.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to upload RadioProgram file to S3.
    """
    try:
        return RadioPrograms.create(
            radio_program=program_in, program_file=program_file.file
        )
    except (DynamoDbClientError, DynamoDbStatusError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store RadioProgram in the DB.",
        )
    except S3ClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to S3.",
        )
    except S3PersistenceError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload RadioProgram file to S3.",
        )


@router.put(
    "/{program_id}",
    response_model=RadioProgramUpdateOutSchema,
    summary="Edit a RadioProgram",
    description="Edit a RadioProgram",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": APIMessage},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": APIMessage},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIMessage},
    },
)
async def update(
    *,
    program_id: uuid.UUID,
    program_in: RadioProgramUpdateInSchema = Depends(
        as_form(RadioProgramUpdateInSchema)
    ),
    program_file: UploadFile = File(None),
) -> Any:
    """Update an existing RadioProgram.

    Args:
        program_id: The UUID of the RadioProgram to modify.
        program_in: The updated RadioProgram.
        program_file: RadioProgram MP3 file.

    Raises:
        HTTPException: HTTP_404_NOT_FOUND
            If RadioProgram does not exist.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to store RadioProgram on DB.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to connect to S3.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to upload RadioProgram file to S3.
    """
    program_file = program_file.file if program_file else None

    try:
        return RadioPrograms.update(
            program_id=program_id, new_program=program_in, program_file=program_file
        )
    except DynamoDbItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadioProgram not found.",
        )
    except (DynamoDbClientError, DynamoDbStatusError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store RadioProgram in the DB.",
        )
    except S3ClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to S3.",
        )
    except S3PersistenceError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload RadioProgram file to S3.",
        )


@router.delete(
    "/{program_id}",
    summary="Delete a RadioProgram",
    description="Delete a RadioProgram",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": APIMessage},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": APIMessage},
    },
)
async def delete(
    *,
    program_id: uuid.UUID,
):
    """Delete an existing Program.

    Args:
        program_id: The UUID of the RadioProgram to delete.

    Raises:
        HTTPException: HTTP_404_NOT_FOUND
            If RadioProgram does not exist.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to delete RadioProgram from DB.
    """
    try:
        RadioPrograms.delete(program_id=program_id)
    except DynamoDbItemNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadioProgram not found.",
        )
    except DynamoDbClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete RadioProgram from the DB.",
        )
