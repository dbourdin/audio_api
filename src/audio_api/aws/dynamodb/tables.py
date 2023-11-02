"""Module containing DynamoDb tables and structures."""

from pydantic import BaseModel

from audio_api.aws.dynamodb.models import RadioProgramItemModel
from audio_api.aws.settings import DynamoDbTables


class DynamoDbTable(BaseModel):
    """DynamoDbTable class with Table properties."""

    table_name: str
    attribute_name: str
    attribute_type: str
    key_type: str
    read_capacity_units: int
    write_capacity_units: int


dynamodb_tables = {
    RadioProgramItemModel: DynamoDbTable(
        table_name=DynamoDbTables.radio_programs,
        attribute_name="id",
        attribute_type="S",
        key_type="HASH",
        read_capacity_units=5,
        write_capacity_units=5,
    )
}
