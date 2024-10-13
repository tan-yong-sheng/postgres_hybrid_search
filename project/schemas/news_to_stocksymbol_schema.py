from pydantic import BaseModel


class NewsToStockSymbolSchema(BaseModel):
    news_id: int
    stock_symbol_id: int


class NewsToStockSymbolCreate(NewsToStockSymbolSchema):
    pass


class NewsToStockSymbolReturn(NewsToStockSymbolSchema):
    id: int
