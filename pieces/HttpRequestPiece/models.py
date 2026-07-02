from pydantic import BaseModel, Field
from enum import Enum
from typing import List


class MethodTypes(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


class InputModel(BaseModel):
    urls: List[str] = Field(
        default=[],
        description="URLs to make requests to."
    )
    method: MethodTypes = Field(
        default=MethodTypes.GET,
        description="HTTP method to use."
    )
    bearer_token: str = Field(
        default=None,
        description="Bearer token to use for authentication."
    )
    body_json_data: str = Field(
        default="""{
    "key_1": "value_1",
    "key_2": "value_2"
}
""",
        description="JSON data to send in the request body.",
        json_schema_extra={
            'widget': "codeeditor-json",
        }
    )


class OutputModel(BaseModel):
    base64_bytes_data: List[str] = Field(
        description='Base64 encoded response bodies for non-image content. Empty strings for image responses.',
    )
    image_file_paths: List[str] = Field(
        default=[],
        description='Paths to saved response files on shared storage, one per URL. Wire this to downstream image pieces.',
    )
