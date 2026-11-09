
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=500,
        description="Plain-text infrastructure management request",
    )


class ChatResponse(BaseModel):
    message: str
    response: str
    status: str
