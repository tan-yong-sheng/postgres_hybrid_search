import pytest
from pydantic import ValidationError

from project.schemas.stocksymbol_schema import StockSymbolCreate


def test_unit_schema_stocksymbol_validation():
    valid_data = {
        "stock_symbol": "GENM",
        "company_name": "Genting Malaysia Berhad",
        "stock_code": "4715",
        "sector": "Consumer Services",
        "subsector": "Hotels, Casinos and Entertainment",
        "mkt": "Main Market",
        "exchange": "KLSE",
    }
    stock_symbol = StockSymbolCreate(**valid_data)
    assert stock_symbol.stock_symbol == "GENM"
    assert stock_symbol.company_name == "Genting Malaysia Berhad"
    assert stock_symbol.stock_code == "4715"
    assert stock_symbol.sector == "Consumer Services"
    assert stock_symbol.subsector == "Hotels, Casinos and Entertainment"
    assert stock_symbol.mkt == "Main Market"
    assert stock_symbol.exchange == "KLSE"

    invalid_data = {"stock_symbol": "GENM"}
    with pytest.raises(ValidationError):
        StockSymbolCreate(**invalid_data)
