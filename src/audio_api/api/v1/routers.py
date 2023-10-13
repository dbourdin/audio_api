"""File that joins all the defined routers to be imported by the main API."""

from fastapi import APIRouter

from audio_api.api.v1.endpoints import programs

router = APIRouter()
router.include_router(programs.router, prefix="/programs", tags=["programs"])
