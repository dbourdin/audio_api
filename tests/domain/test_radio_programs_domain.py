"""Test TestRadioProgramsDomain."""

import unittest

import pytest

from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.domain.radio_programs import RadioPrograms


@pytest.mark.usefixtures("localstack")
@pytest.mark.usefixtures("radio_programs")
@pytest.mark.usefixtures("radio_programs_repository")
@pytest.mark.usefixtures("create_program_model")
class TestRadioProgramsDomain(unittest.TestCase):
    """TestRadioProgramsDomain class."""

    radio_programs: RadioPrograms
    radio_programs_repository: RadioProgramsRepository
    create_program_model: RadioProgramPutItemModel

    def test_get_radio_program(self):
        """Should retrieve an existing RadioProgram."""
        # Given
        created_radio_program = self.radio_programs_repository.put_item(
            self.create_program_model
        )

        # When
        db_radio_program = self.radio_programs.get(program_id=created_radio_program.id)

        # Then
        assert db_radio_program == created_radio_program
