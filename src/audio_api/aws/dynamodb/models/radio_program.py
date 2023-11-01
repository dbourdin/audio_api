"""RadioProgram DynamoDB Models."""

from audio_api.aws.dynamodb.models import (
    DynamoDbItemModel,
    DynamoDbPutItemModel,
    DynamoDbUpdateItemModel,
)


class RadioProgramItemModel(DynamoDbItemModel):
    """RadioProgramItemModel class."""


class RadioProgramPutItemModel(DynamoDbPutItemModel):
    """RadioProgramPutItemModel class."""


class RadioProgramUpdateItemModel(DynamoDbUpdateItemModel):
    """RadioProgramUpdateItemModel class."""
