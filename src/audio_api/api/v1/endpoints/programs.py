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
    summary="List Users",
    description="Get a list of Users",
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
