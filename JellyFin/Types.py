from typing import TypedDict
from requests import Response

class ErrorResponse(TypedDict):
    message: str
    response: Response