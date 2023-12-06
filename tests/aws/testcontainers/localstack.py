"""Module containing LocalStack Container."""
import unittest
from urllib.parse import urlparse

import pytest
from testcontainers.localstack import LocalStackContainer as LocalStackContainer_

from audio_api.aws.dynamodb.repositories.base_repository import BaseDynamoDbRepository
from audio_api.aws.dynamodb.tables import dynamodb_tables
from audio_api.aws.s3.repositories.base_repository import BaseS3Repository
from audio_api.aws.settings import AwsResources, S3Buckets, get_settings

settings = get_settings()
localstack_port = urlparse(settings.AWS_ENDPOINT_URL).port


class LocalStackContainer(LocalStackContainer_):
    """LocalStackContainer implementation class."""

    s3_client = BaseS3Repository.get_s3_client()
    dynamodb_client = BaseDynamoDbRepository.get_dynamodb_client()

    def _create_buckets(self):
        for bucket in S3Buckets:
            self.s3_client.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={
                    "LocationConstraint": settings.AWS_DEFAULT_REGION
                },
            )

    def _create_dynamodb_tables(self):
        for table in dynamodb_tables.values():
            self.dynamodb_client.create_table(
                TableName=table.table_name,
                AttributeDefinitions=[
                    {
                        "AttributeName": table.attribute_name,
                        "AttributeType": table.attribute_type,
                    },
                ],
                KeySchema=[
                    {
                        "AttributeName": table.attribute_name,
                        "KeyType": table.key_type,
                    },
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": table.read_capacity_units,
                    "WriteCapacityUnits": table.write_capacity_units,
                },
            )

    def start(self, **kwargs):
        """Start the localstack container."""
        super().start(**kwargs)
        try:
            self._create_buckets()
            self._create_dynamodb_tables()
        except Exception as e:
            self.stop()
            raise e

        return self


localstack_container = LocalStackContainer(image="localstack/localstack:2.3.2")
localstack_container.with_bind_ports(localstack_port, localstack_port)
localstack_container.with_services(AwsResources.s3, AwsResources.dynamodb)


class LocalStackContainerTest(unittest.TestCase):
    """LocalStackContainerTest class."""

    _localstack_container = localstack_container

    @pytest.fixture(scope="class", autouse=True)
    def localstack_container(self):
        """Start and stop localstack container."""
        with self._localstack_container:
            yield self._localstack_container
