"""Base Schemas used across the whole API."""

from fastapi_utils.api_model import APIModel


class APISchema(APIModel):
    """Base schema that can be created using snake_case and camelCase params.

    All schemas should inherit from this one instead of Pydantic's BaseModel.
    """


class APIMessage(APISchema):
    """Simple message schema used to return information to the user."""

    detail: str
