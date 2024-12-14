"""Module containing LocalStack Container."""
from urllib.parse import urlparse

from testcontainers.localstack import LocalStackContainer as LocalStackContainer_

from audio_api.aws.aws_service import AwsService, AwsServices
from audio_api.aws.dynamodb.tables import dynamodb_tables
from audio_api.aws.settings import S3Buckets, get_settings

settings = get_settings()
localstack_port = urlparse(settings.AWS_ENDPOINT_URL).port


class LocalStackContainer(LocalStackContainer_):
    """LocalStackContainer implementation class."""

    s3_client = AwsService(AwsServices.s3).get_client()
    dynamodb_client = AwsService(AwsServices.dynamodb).get_client()

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
localstack_container.with_services(AwsServices.s3, AwsServices.dynamodb)
