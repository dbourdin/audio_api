"""BaseDynamoDbRepository class."""
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

import boto3
from boto3.dynamodb.conditions import Key
from botocore.client import BaseClient
from pydantic import BaseModel

from audio_api.aws.settings import AwsResource, DynamoDbTables, get_settings

settings = get_settings()


ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDynamoDbRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """BaseBaseDynamoDbRepository class."""

    def __init__(
        self,
        model: type[ModelType],
        table: DynamoDbTables,
    ):
        """Repository with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: A pydantic BaseModel class.
            table: A DynamoDB table.
        """
        self.model = model
        self.dynamodb_client = self.get_dynamodb_client()
        self.dynamodb_resource = self.get_dynamodb_resource()
        # TODO: Bound table to Schema and get from there.
        self.table = self.dynamodb_resource.Table(table)

    @classmethod
    def get_dynamodb_client(cls) -> BaseClient:
        """Return a DynamoDB Client configured with boto3."""
        return boto3.client(
            AwsResource.DYNAMODB,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    @classmethod
    def get_dynamodb_resource(cls):
        """Return a DynamoDB Resource configured with boto3."""
        return boto3.resource(
            AwsResource.DYNAMODB,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    @classmethod
    def _build_update_query_expression(cls, update_item: ModelType) -> dict:
        def _build_update_item_dict(item: BaseModel):
            def _parse_value(val: Any):
                if isinstance(val, dict):
                    return {k: _parse_value(v) for k, v in val.items() if v}
                return val

            return _parse_value(item.dict())

        update_item_dict = _build_update_item_dict(update_item)
        attributes = {
            param: {"name": f"#{param}", "value": value, "expression": f":{param}_"}
            for param, value in update_item_dict.items()
        }

        attribute_names = {
            param["name"]: param_name for param_name, param in attributes.items()
        }
        attribute_values = {
            param["expression"]: param["value"] for param in attributes.values()
        }
        update_values = [
            f" {param['name']} = {param['expression']}" for param in attributes.values()
        ]
        update_expression = "SET" + ",".join(update_values)

        return {
            "attribute_names": attribute_names,
            "attribute_values": attribute_values,
            "update_expression": update_expression,
        }

    def get(self, id: UUID) -> type[ModelType] | None:
        """Get a single DynamoDB record by id.

        Args:
            id: The id to retrieve.

        Returns:
            Optional[ModelType]: The retrieved record.
        """
        key_condition = Key("id").eq(str(id))

        result_query = self.table.query(
            ScanIndexForward=False, KeyConditionExpression=key_condition
        )["Items"]

        if result_query:
            return self.model(**result_query[0])

    def get_all(self) -> list[type[ModelType]]:
        """Get all DynamoDB records in the table.

        Returns:
            list[ModelType]: List containing all received attributes.
        """
        return [self.model(**item) for item in self.table.scan().get("Items", [])]

    def create(self, item: CreateSchemaType) -> type[ModelType] | None:
        """Create a new item to DynamoDB table.

        Args:
            item: Item to be inserted in DynamoDB table.

        Returns:
            ModelType: Retrieved item from DynamoDB.
        """
        item_dict = item.dict()
        item_dict["id"] = str(uuid4())

        self.table.put_item(Item=item_dict)

        return self.model(**item_dict)

    def update(self, id: UUID, item: UpdateSchemaType) -> type[ModelType]:
        """Update an existing item in DynamoDB table.

        Args:
            id: Item id to be updated.
            item: Model containing updated data.

        Returns:
            dict containing the updated solution.
        """
        update_query = self._build_update_query_expression(item)
        result = self.table.update_item(
            Key={"id": str(id)},
            ConditionExpression="attribute_exists(id)",
            ExpressionAttributeNames=update_query["attribute_names"],
            ExpressionAttributeValues=update_query["attribute_values"],
            UpdateExpression=update_query["update_expression"],
            ReturnValues="ALL_NEW",
        )

        return self.model(**result["Attributes"])

    def remove(self, id: UUID) -> type[ModelType]:
        """Delete an item from the DynamoDB table based on the provided id.

        Args:
            id: Item id to be deleted from DynamoDB table.

        Returns:
            ModelType containing result from delete query to dynamoDB.
        """
        result = self.table.delete_item(
            Key={"id": str(id)}, ConditionExpression="attribute_exists(id)"
        )
        return self.model(**result)
