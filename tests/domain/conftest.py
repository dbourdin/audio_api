"""TestRadioProgramsDomain fixtures."""

import pytest

from audio_api.domain.radio_programs import RadioPrograms


@pytest.fixture(scope="class")
def radio_programs(request) -> type[RadioPrograms]:
    """Return RadioPrograms domain."""
    request.cls.radio_programs = RadioPrograms
    return RadioPrograms
