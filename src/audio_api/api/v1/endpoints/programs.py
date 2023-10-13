"""Endpoints related to Radio Programs."""

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from audio_api import schemas
from audio_api.api import deps

router = APIRouter()


@router.get(
    "/{program_id}",
    response_model=schemas.ProgramGet,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": schemas.APIMessage},
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
    """
    program = schemas.ProgramGet(
        uuid=uuid.uuid4(),
        title="Shopping 2.0 #1",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    return program


@router.get(
    "",
    response_model=list[schemas.ProgramList],
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
    programs = [
        schemas.ProgramList(
            uuid=uuid.uuid4(),
            title="Shopping 2.0 #1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        schemas.ProgramList(
            uuid=uuid.uuid4(),
            title="Shopping 2.0 #2",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    return programs


@router.post(
    "",
    response_model=schemas.ProgramCreateOut,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {"model": schemas.APIMessage}},
    summary="Create a Program",
    description="Create a Program",
)
async def create(
    *,
    db: Session = Depends(deps.get_db),
    program_in: schemas.ProgramCreateIn,
) -> Any:
    """Create a new program.

    Args:
        db (Session): A database session
        program_in (schemas.ProgramCreateIn): Input data
    """
    db_program = schemas.ProgramCreateOut(
        uuid=uuid.uuid4(),
        title=program_in.title,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return db_program


@router.put(
    "/{program_id}",
    response_model=schemas.ProgramUpdateOut,
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
    program_in: schemas.ProgramUpdateIn,
) -> Any:
    """Update an existing Program.

    Args:
        db (Session): A database session
        program_id (uuid.UUID): The uuid of the program to modify
        program_in (schemas.ProgramUpdateIn): The new data
    """
    updated_instance = schemas.ProgramUpdateOut(
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
) -> Any:
    """Delete an existing Program.

    Args:
        db (Session): A database session
        program_id (uuid.UUID): The uuid of the program to delete
    """
