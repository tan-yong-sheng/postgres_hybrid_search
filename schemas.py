from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StockSymbolSchema(BaseModel):
    stock_symbol: str
    company_name: str
    stock_code: str
    sector: str
    subsector: str
    mkt: str
    exchange: str
    company_description: Optional[str] = None


class StockSymbolCreate(StockSymbolSchema):
    pass


class ExtractTicker(BaseModel):
    # specifically used for the train_extract_tickers.py script
    stock_symbol: str
    company_name: str
    stock_code: str


class StockSymbolReturn(StockSymbolSchema):
    id: int


class NewsToStockSymbolSchema(BaseModel):
    news_id: int
    stock_symbol_id: int


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


class NewsChunksSchema(BaseModel):
    chunk_content: str
    news_id: int
    embedding: list[float]


class NewsChunksReturn(NewsChunksSchema):
    id: int
