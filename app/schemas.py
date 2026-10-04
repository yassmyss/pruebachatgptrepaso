from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)


class Source(BaseModel):
    source: str
    excerpt: str


class AskResponse(BaseModel):
    category: str
    answer: str
    sources: list[Source]
