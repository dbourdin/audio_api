"""Endpoints related to Radio Programs."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from audio_api import schemas
from audio_api.domain.radio_programs_dynamo import RadioPrograms
from audio_api.persistence.repositories.radio_program import (
    RadioProgramAlreadyExistsError,
    RadioProgramDatabaseError,
    RadioProgramNotFoundError,
)
from audio_api.s3.program_file_persistence import RadioProgramS3Error
from audio_api.schemas.utils import as_form

router = APIRouter()


@router.get(
    "/{program_id}",
    response_model=schemas.RadioProgramGet,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": schemas.RadioProgramGet},
    },
    summary="Retrieve a single RadioProgram by UUID",
    description="Retrieve single a RadioProgram by UUID",
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
    except RadioProgramNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadioProgram not found.",
        )
    except RadioProgramDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve RadioProgram from the DB.",
        )


@router.get(
    "",
    response_model=list[schemas.RadioProgramList],
    summary="List RadioProgram",
    description="Get a list of RadioProgram",
)
def get_all() -> Any:
    """Retrieve all RadioProgram.

    Raises:
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to retrieve RadioPrograms.
    """
    try:
        return RadioPrograms.get_all()
    except RadioProgramDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve RadioPrograms from the DB.",
        )


@router.post(
    "",
    response_model=schemas.RadioProgramCreateOut,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {"model": schemas.APIMessage}},
    summary="Create a RadioProgram",
    description="Create a RadioProgram",
)
async def create(
    *,
    program_in: schemas.RadioProgramCreateIn = Depends(
        as_form(schemas.RadioProgramCreateIn)
    ),
    program_file: UploadFile = File(...),
) -> Any:
    """Create a new RadioProgram.

    Args:
        program_in: New RadioProgram.
        program_file: RadioProgram MP3 file.

    Raises:
        HTTPException: HTTP_400_BAD_REQUEST
            If RadioProgram already exists.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to store RadioProgram on DB.
        HTTPException: HTTP_500_INTERNAL_SERVER_ERROR
            If failed to upload RadioProgram file to S3.
    """
    try:
        return RadioPrograms.create(
            radio_program=program_in, program_file=program_file.file
        )
    except RadioProgramAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RadioProgram already exists.",
        )
    except RadioProgramDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store RadioProgram in the DB.",
        )
    except RadioProgramS3Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload RadioProgram file to S3.",
        )


@router.put(
    "/{program_id}",
    response_model=schemas.RadioProgramUpdateOut,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": schemas.APIMessage},
    },
    summary="Edit a RadioProgram",
    description="Edit a RadioProgram",
)
async def update(
    *,
    program_id: uuid.UUID,
    program_in: schemas.RadioProgramUpdateIn = Depends(
        as_form(schemas.RadioProgramUpdateIn)
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
            If failed to upload RadioProgram file to S3.
    """
    update_args = {
        "program_id": program_id,
        "new_program": program_in,
    }
    if program_file:
        update_args["program_file"] = program_file.file

    try:
        return RadioPrograms.update(**update_args)
    except RadioProgramNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadioProgram not found.",
        )
    except RadioProgramDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store RadioProgram in the DB.",
        )
    except RadioProgramS3Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload RadioProgram file to S3.",
        )


@router.delete(
    "/{program_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": schemas.APIMessage},
    },
    summary="Delete a RadioProgram",
    description="Delete a RadioProgram",
    status_code=status.HTTP_204_NO_CONTENT,
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
        RadioPrograms.remove(program_id=program_id)
    except RadioProgramNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RadioProgram not found.",
        )
    except RadioProgramDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete RadioProgram from the DB.",
        )
