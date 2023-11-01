"""DynamoDbItemBaseSchema class."""
from audio_api.schemas import APISchema


class DynamoDbItemBaseSchema(APISchema):
    """DynamoDbItemBaseSchema class."""


class DynamoDbPutItemSchema(DynamoDbItemBaseSchema):
    """DynamoDbPutItemSchema class."""


class DynamoDbUpdateItemSchema(DynamoDbItemBaseSchema):
    """DynamoDbUpdateItemSchema class."""
