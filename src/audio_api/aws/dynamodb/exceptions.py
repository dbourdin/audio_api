"""DynamoDB Exceptions."""


class DynamoDbClientError(Exception):
    """DynamoDbClientError class to handle DynamoDB errors."""


class DynamoDbItemNotFoundError(Exception):
    """DynamoDbItemNotFoundError class to handle DynamoDB errors."""


class DynamoDbStatusError(Exception):
    """DynamoDbStatusError class to handle DynamoDB errors."""
