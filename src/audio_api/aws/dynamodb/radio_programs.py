"""RadioProgramRepository to handle DynamoDB persistence."""

from uuid import UUID

from audio_api.aws.dynamodb.repositories.base_repository import BaseDynamoDbRepository
from audio_api.aws.settings import DynamoDbTables
from audio_api.schemas import RadioProgram, RadioProgramCreateDB, RadioProgramUpdateDB


class RadioProgramDatabaseError(Exception):
    """RadioProgramDatabaseError class to handle DB errors."""


# TODO: This Exc goes in Domain
class RadioProgramNotFoundError(Exception):
    """RadioProgramNotFoundError class."""


class RadioProgramAlreadyExistsError(Exception):
    """RadioProgramAlreadyExistsError class."""


class RadioProgramsRepository(
    BaseDynamoDbRepository[RadioProgram, RadioProgramCreateDB, RadioProgramUpdateDB]
):
    """RadioProgramsRepository to handle DB persistence."""

    def get(self, program_id: UUID) -> RadioProgram:
        """Get a RadioProgram program by program_id.

        Args:
            program_id (UUID): The program_id to retrieve.

        Raises:
            RadioProgramNotFoundError: If the program is not found.

        Returns:
            RadioProgram: The retrieved radio program.
        """
        db_program = super().get(id=program_id)

        # TODO: THIS SHOULD BE IN DOMAIN
        if db_program is None:
            raise RadioProgramNotFoundError(
                f"Couldn't find RadioProgram with id: {program_id}"
            )

        return db_program

    def create(self, radio_program: RadioProgramCreateDB) -> RadioProgram:
        """Create a new RadioProgram.

        Args:
            radio_program: RadioProgram to be created.

        Raises:
            RadioProgramDatabaseError: If failed to store new RadioProgram.

        Returns:
            RadioProgram: The created RadioProgram.
        """
        try:
            return super().create(item=radio_program)
        # TODO: Check DynamoDB Exceptions.
        except Exception as e:
            raise RadioProgramDatabaseError(f"Failed to create new RadioProgram: {e}")

    def update(
        self,
        program_id: UUID,
        updated_program: RadioProgramUpdateDB,
    ) -> RadioProgram:
        """Update an existing RadioProgram.

        Args:
            program_id: Existing RadioProgram in the DB.
            updated_program: Updated RadioProgram instance.

        Raises:
            RadioProgramDatabaseError: If failed to update RadioProgram.

        Returns:
            RadioProgram: The updated RadioProgram properties.
        """
        try:
            return super().update(id=program_id, item=updated_program)
        except Exception as e:
            raise RadioProgramDatabaseError(
                f"Failed to update RadioProgram {program_id}: {e}"
            )

    def remove(self, program_id: UUID) -> RadioProgram:
        """Remove an existing RadioProgram from the DB.

        Args:
            program_id: RadioProgram id to be removed.

        Raises:
            RadioProgramDatabaseError: If failed to remove existing RadioProgram.

        Returns:
            RadioProgram: The removed RadioProgram.
        """
        try:
            return super().remove(id=program_id)
        except Exception as e:
            raise RadioProgramDatabaseError(
                f"Failed to remove existing RadioProgram: {e}"
            )


radio_programs_repository = RadioProgramsRepository(
    RadioProgram, DynamoDbTables.RadioPrograms
)
