"""Endpoints related to Radio Programs."""

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from audio_api import schemas
from audio_api.api import deps
from audio_api.persistence.repositories import radio_programs

router = APIRouter()


@router.get(
    "/{program_id}",
    response_model=schemas.RadioProgramGet,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": schemas.RadioProgramGet},
    },
    summary="Retrieve a single Program by UUID",
    description="Retrieve single a Program by UUID",
)
async def get(
    *,
    db: Session = Depends(deps.get_db),
    program_id: uuid.UUID,
) -> Any:
    """Retrieve an existing Program.

    Args:
        db (Session): A database session
        program_id (uuid.UUID): The uuid of the program to retrieve

    Raises:
        HTTPException: HTTP_404_NOT_FOUND: If the radio program does not exist.
    """
    db_program = radio_programs.get_by_program_id(db, program_id=program_id)
    if db_program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Radio program not found",
        )
    return db_program


@router.get(
    "",
    response_model=list[schemas.RadioProgramList],
    summary="List Programs",
    description="Get a list of Programs",
)
def retrieve_many(
    db: Session = Depends(deps.get_db),
) -> Any:
    """Retrieve many programs.

    Args:
        db (Session): A database session
    """
    db_programs = radio_programs.get_multi(db)
    return db_programs


@router.post(
    "",
    response_model=schemas.RadioProgramCreateOut,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {"model": schemas.APIMessage}},
    summary="Create a Program",
    description="Create a Program",
)
async def create(
    *,
    db: Session = Depends(deps.get_db),
    program_in: schemas.RadioProgramCreateIn,
) -> Any:
    """Create a new program.

    Args:
        db (Session): A database session
        program_in (schemas.RadioProgramCreateIn): Input data

    Raises:
        HTTPException: HTTP_400_BAD_REQUEST: If failed to create radio program.
    """
    try:
        db_program = radio_programs.create(db, obj_in=program_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create new radio program",
        )
    return db_program


@router.put(
    "/{program_id}",
    response_model=schemas.RadioProgramUpdateOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": schemas.APIMessage},
        status.HTTP_404_NOT_FOUND: {"model": schemas.APIMessage},
    },
    summary="Edit a Program",
    description="Edit a Program",
)
async def update(
    *,
    db: Session = Depends(deps.get_db),
    program_id: uuid.UUID,
    program_in: schemas.RadioProgramUpdateIn,
) -> Any:
    """Update an existing Program.

    Args:
        db (Session): A database session
        program_id (uuid.UUID): The uuid of the program to modify
        program_in (schemas.RadioProgramUpdateIn): The new data
    """
    updated_instance = schemas.RadioProgramUpdateOut(
        uuid=program_id,
        title=program_in.title,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    return updated_instance


@router.delete(
    "/{program_id}",
    responses={
        status.HTTP_403_FORBIDDEN: {"model": schemas.APIMessage},
        status.HTTP_404_NOT_FOUND: {"model": schemas.APIMessage},
    },
    summary="Delete a Program",
    description="Delete a Program",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    *,
    db: Session = Depends(deps.get_db),
    program_id: uuid.UUID,
):
    """Delete an existing Program.

    Args:
        db (Session): A database session
        program_id (uuid.UUID): The uuid of the program to delete
    """
