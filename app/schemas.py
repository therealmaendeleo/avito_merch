from pydantic import BaseModel


class BaseResponse(BaseModel):
    code: int
    message: str


class BaseErrorResponse(BaseModel):
    code: int
    detail: str
