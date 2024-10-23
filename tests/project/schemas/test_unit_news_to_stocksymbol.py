import pytest
from pydantic import ValidationError

from project.schemas.news_to_stocksymbol_schema import NewsToStockSymbolCreate


def test_unit_schema_news_to_stocksymbol_validation():
    valid_data = {"news_id": 1083, "stock_symbol_id": 54}
    news_to_stocksymbol = NewsToStockSymbolCreate(**valid_data)
    assert news_to_stocksymbol.news_id == 1083
    assert news_to_stocksymbol.stock_symbol_id == 54

    invalid_data = {"news_id": 1083, "stock_symbol_id": None}
    with pytest.raises(ValidationError):
        _ = NewsToStockSymbolCreate(**invalid_data)
