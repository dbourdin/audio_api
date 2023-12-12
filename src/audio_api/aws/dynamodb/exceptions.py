"""DynamoDB Exceptions."""


class DynamoDbClientError(Exception):
    """DynamoDbClientError class to handle DynamoDB errors."""


class DynamoDbPersistenceError(Exception):
    """DynamoDbPersistenceError class to handle DynamoDB errors."""


class DynamoDbItemNotFoundError(Exception):
    """DynamoDbItemNotFoundError class to handle DynamoDB errors."""
