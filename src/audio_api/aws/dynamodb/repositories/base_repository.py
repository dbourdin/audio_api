"""BaseDynamoDbRepository class."""
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

import boto3
from boto3.dynamodb.conditions import Key
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from pydantic import BaseModel

from audio_api.aws.dynamodb.exceptions import DynamoDbClientError
from audio_api.aws.dynamodb.models import (
    DynamoDbItemModel,
    DynamoDbPutItemModel,
    DynamoDbUpdateItemModel,
)
from audio_api.aws.dynamodb.tables import dynamodb_tables
from audio_api.aws.settings import AwsResources, get_settings
from audio_api.logger.logger import get_logger

logger = get_logger("dynamodb_repository")
settings = get_settings()


ModelType = TypeVar("ModelType", bound=DynamoDbItemModel)
PutItemModelType = TypeVar("PutItemModelType", bound=DynamoDbPutItemModel)
UpdateItemModelType = TypeVar("UpdateItemModelType", bound=DynamoDbUpdateItemModel)


class BaseDynamoDbRepository(Generic[ModelType, PutItemModelType, UpdateItemModelType]):
    """BaseBaseDynamoDbRepository class."""

    def __init__(
        self,
        model: type[ModelType],
    ):
        """Repository with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: A DynamoDbItemModel class.
        """
        self.model = model
        self.dynamodb_client = self.get_dynamodb_client()
        self.dynamodb_resource = self.get_dynamodb_resource()
        self.table_name = dynamodb_tables[self.model].table_name
        self.table = self.dynamodb_resource.Table(self.table_name)

    @classmethod
    def get_dynamodb_client(cls) -> BaseClient:
        """Return a DynamoDB Client configured with boto3."""
        return boto3.client(
            AwsResources.dynamodb,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    @classmethod
    def get_dynamodb_resource(cls):
        """Return a DynamoDB Resource configured with boto3."""
        return boto3.resource(
            AwsResources.dynamodb,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    @classmethod
    def _build_update_query_expression(cls, update_item: ModelType) -> dict:
        """Build a dict with the update query parameters from a pydantic BaseModel.

        Args:
              update_item: Model containing the values to update.

        Returns:
              dict: Containing the update_query values used in update_item.
        """

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

    def get_item(self, item_id: UUID) -> type[ModelType] | None:
        """Get a single DynamoDB item by item_id.

        Args:
            item_id: The item_id to retrieve.

        Raises:
            DynamoDbClientError: If failed to get item from DynamoDB.

        Returns:
            Optional[ModelType]: The retrieved item.
        """
        key_condition = Key("id").eq(str(item_id))

        try:
            result_query = self.table.query(
                ScanIndexForward=False, KeyConditionExpression=key_condition
            )["Items"]
        # TODO: Test this Exception!
        except ClientError as e:
            logger.error(f"Failed to get_item {item_id} from {self.table_name} table.")
            raise DynamoDbClientError(f"Failed to get item from DynamoDB: {e}")

        if result_query:
            return self.model(**result_query[0])

    def get_items(self) -> list[type[ModelType]]:
        """Get all DynamoDB items in the table.

        Raises:
            DynamoDbClientError: If failed to get items from DynamoDB.

        Returns:
            list[ModelType]: List containing all received items.
        """
        try:
            items = [self.model(**item) for item in self.table.scan().get("Items", [])]
        # TODO: Test this Exception!
        except ClientError as e:
            logger.error(f"Failed to get_items from {self.table_name} table.")
            raise DynamoDbClientError(f"Failed to get items from DynamoDB: {e}")

        return items

    def put_item(self, item: PutItemModelType) -> type[ModelType]:
        """Create a new item to DynamoDB table.

        Args:
            item: Item to be inserted in DynamoDB table.

        Raises:
            DynamoDbClientError: If failed to store new item in DynamoDB.

        Returns:
            ModelType: Retrieved item from DynamoDB.
        """
        item_dict = item.dict()
        item_id = str(uuid4())
        item_dict["id"] = item_id

        try:
            self.table.put_item(Item=item_dict)
        # TODO: Test this Exception!
        except ClientError as e:
            logger.error(f"Failed to put_item {item_id} on {self.table_name} table.")
            raise DynamoDbClientError(f"Failed to store new item in DynamoDB: {e}")

        logger.info(f"Successfully put_item {item_id} on {self.table_name} table.")
        # TODO: Can model be read from response instead??
        return self.model(**item_dict)

    def update_item(self, item_id: UUID, item: UpdateItemModelType) -> type[ModelType]:
        """Update an existing item in DynamoDB table.

        Args:
            item_id: Item id to be updated.
            item: Model containing updated data.

        Raises:
            DynamoDbClientError: If failed to update item in DynamoDB.

        Returns:
            dict containing the updated solution.
        """
        update_query = self._build_update_query_expression(item)

        try:
            result = self.table.update_item(
                Key={"id": str(item_id)},
                ConditionExpression="attribute_exists(id)",
                ExpressionAttributeNames=update_query["attribute_names"],
                ExpressionAttributeValues=update_query["attribute_values"],
                UpdateExpression=update_query["update_expression"],
                ReturnValues="ALL_NEW",
            )
        # TODO: Test this Exception!
        except ClientError as e:
            logger.error(f"Failed to update_item {item_id} on {self.table_name} table.")
            raise DynamoDbClientError(f"Failed to update item in DynamoDB: {e}")

        logger.info(f"Successfully update_item {item_id} on {self.table_name} table.")
        return self.model(**result["Attributes"])

    def delete_item(self, item_id: UUID) -> None:
        """Delete an item from the DynamoDB table based on the provided id.

        Args:
            item_id: Item id to be deleted from DynamoDB table.

        Raises:
            DynamoDbClientError: If failed to delete item from DynamoDB.
        """
        try:
            response = self.table.delete_item(
                Key={"id": str(item_id)}, ConditionExpression="attribute_exists(id)"
            )
        except ClientError as e:
            logger.error(f"Failed to delete_item {item_id} on {self.table_name} table.")
            raise DynamoDbClientError(f"Failed to delete item from DynamoDB: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status == 200:
            logger.info(
                f"Successfully delete_item {item_id} on {self.table_name} table."
            )
        else:
            # TODO: Should raise some exception??
            logger.error(
                f"Failed to delete_item {item_id} from {self.table_name} table."
            )

    def delete_all(self) -> None:
        """Delete all objects from dynamodb table."""
        scan = self.table.scan(
            ProjectionExpression="#k",
            ExpressionAttributeNames={"#k": "id"},
        )

        with self.table.batch_writer() as batch:
            for each in scan.get("Items", []):
                batch.delete_item(Key=each)
