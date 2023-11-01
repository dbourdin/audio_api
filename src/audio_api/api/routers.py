"""File that joins all the defined routers to be imported by the main API."""

from fastapi import APIRouter

from audio_api.api.endpoints import radio_programs

router = APIRouter()
router.include_router(radio_programs.router, prefix="/programs", tags=["programs"])
