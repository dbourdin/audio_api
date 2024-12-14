"""RadioProgram DynamoDB Models."""

from audio_api.aws.dynamodb.models import (
    DynamoDbItemModel,
    DynamoDbPutItemModel,
    DynamoDbUpdateItemModel,
)
from audio_api.domain.models import (
    BaseRadioProgramModel,
    RadioProgramFileModel,
    RadioProgramModel,
)


class RadioProgramItemModel(DynamoDbItemModel, RadioProgramModel):
    """RadioProgramItemModel class."""


class RadioProgramPutItemModel(DynamoDbPutItemModel, BaseRadioProgramModel):
    """RadioProgramPutItemModel class."""


class RadioProgramUpdateItemModel(DynamoDbUpdateItemModel, BaseRadioProgramModel):
    """RadioProgramUpdateItemModel class."""

    radio_program: RadioProgramFileModel | None
