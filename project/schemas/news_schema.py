from datetime import datetime

from . import BaseModel


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


class NewsSearchReturn(BaseModel):
    title: str
    content: str
    score: float
