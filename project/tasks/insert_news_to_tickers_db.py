from typing import Iterable

from project.db_connection import db_context
from project.db_models import NewsOrm, NewsToStockSymbol
from project.schemas.news_to_stocksymbol_schema import (
    NewsToStockSymbolCreate,
    NewsToStockSymbolReturn,
)
from project.tasks.recognize_financial_entities import (
    extract_financial_entities_from_news_db,
    perform_trigram_search_on_financial_entities,
)


def check_existing_news_to_stock_symbol(
    news_id: int, stock_symbol_id: int
) -> NewsToStockSymbolReturn:
    """Check if the uploaded data has the same news record, with same stock_id"""
    with db_context() as db_session:
        existing_news_to_stock_symbol = (
            db_session.query(NewsToStockSymbol)
            .filter(
                NewsToStockSymbol.news_id == news_id,
                NewsToStockSymbol.stock_symbol_id == stock_symbol_id,
            )
            .first()
        )
        return existing_news_to_stock_symbol


def generate_news_to_stock_symbol() -> Iterable[dict]:
    news_items = extract_financial_entities_from_news_db()

    for item in news_items:
        stock_symbol_ids = perform_trigram_search_on_financial_entities(
            exchange_market=item["exchange"],
            entity_name=item["entity_name"],
            entity_type=item["entity_type"],
        )

        yield {
            "news_id": item["news_id"],
            "stock_symbol_id": stock_symbol_ids["stock_id"],
        }


def insert_news_to_stock_symbol(news_id: int, stock_symbol_id: int):
    """Insert news id with stock id, generated by `recognize_financial_entities.py` script"""

    existing_news_to_stock_symbol = check_existing_news_to_stock_symbol(
        news_id, stock_symbol_id
    )
    if not existing_news_to_stock_symbol:
        with db_context() as db_session:
            news_to_stock_symbol_dict = NewsToStockSymbolCreate(
                news_id=news_id, stock_symbol_id=stock_symbol_id
            )
            news_to_stock_symbol_obj = NewsToStockSymbol(
                **news_to_stock_symbol_dict.__dict__
            )
            db_session.add(news_to_stock_symbol_obj)
            db_session.commit()


def update_news_is_ticker_checked(news_id: int):
    """Update the `is_ticker_checked` column to True for the `news` table"""

    with db_context() as db_session:
        news = db_session.query(NewsOrm).filter(NewsOrm.id == news_id).first()
        news.is_ticker_checked = True
        db_session.commit()


if __name__ == "__main__":
    news_to_stock_symbols = generate_news_to_stock_symbol()

    for news_to_stock_symbol in news_to_stock_symbols:
        if news_to_stock_symbol["stock_symbol_id"] is not None:
            _ = insert_news_to_stock_symbol(
                news_to_stock_symbol["news_id"], news_to_stock_symbol["stock_symbol_id"]
            )
        # Update the `is_ticker_checked` column to True for the `news` table
        _ = update_news_is_ticker_checked(news_to_stock_symbol["news_id"])
