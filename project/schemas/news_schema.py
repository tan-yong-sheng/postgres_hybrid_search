from datetime import datetime
from typing import Optional

from pydantic import BaseModel, conlist


class NewsSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
    title: str
    content: str
    url: str
    is_ticker_checked: bool = False
    # ensure the length of the embedding list is 384
    embedding: Optional[conlist(float, min_length=384, max_length=384)] = None  # type: ignore


class NewsCreate(NewsSchema):
    pass


class NewsReturn(NewsSchema):
    id: int


class NewsSearchReturn(BaseModel):
    title: str
    created_at: datetime
    content: str
    score: float
