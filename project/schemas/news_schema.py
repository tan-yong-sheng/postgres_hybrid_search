from datetime import datetime

from pydantic import BaseModel


class NewsSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
    title: str
    content: str
    url: str


class NewsCreate(NewsSchema):
    pass


class NewsReturn(NewsSchema):
    id: int
