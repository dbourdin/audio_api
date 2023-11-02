"""RadioProgramsRepository class."""

from audio_api.aws.dynamodb.models import (
    RadioProgramItemModel,
    RadioProgramPutItemModel,
    RadioProgramUpdateItemModel,
)
from audio_api.aws.dynamodb.repositories import BaseDynamoDbRepository
from audio_api.aws.settings import DynamoDbTables


class RadioProgramsRepository(
    BaseDynamoDbRepository[
        RadioProgramItemModel, RadioProgramPutItemModel, RadioProgramUpdateItemModel
    ]
):
    """RadioProgramsRepository class."""


radio_programs_repository = RadioProgramsRepository(
    RadioProgramItemModel, DynamoDbTables.radio_programs
)
