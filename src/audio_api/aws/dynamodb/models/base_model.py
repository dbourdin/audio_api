"""DynamoDbItemBaseModel classes."""
from pydantic import BaseModel


class DynamoDbItemModel(BaseModel):
    """DynamoDbItemBaseModel class."""


class DynamoDbPutItemModel(BaseModel):
    """DynamoDbPutItemModel class."""


class DynamoDbUpdateItemModel(BaseModel):
    """DynamoDbUpdateItemSchema class."""
