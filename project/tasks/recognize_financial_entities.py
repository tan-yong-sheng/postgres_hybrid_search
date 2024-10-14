import logging
from typing import Literal

from sqlalchemy.sql.expression import desc, false, func

from project.db_connection import db_context
from project.db_models import NewsOrm, StockSymbolOrm
from project.schemas.exchange_schema import ExchangeSchema
from project.utils.nlp_handler import extract_financial_entities

logger = logging.getLogger(__name__)


def extract_financial_entities_from_news_db():
    with db_context() as db_session:
        news_content_without_ticker_checked = (
            db_session.query(NewsOrm).filter(NewsOrm.is_ticker_checked == false()).all()
        )

        if not news_content_without_ticker_checked:
            logger.info(
                "No news content to be processed to get stock symbols, stock code or company names"
            )
            return

        for news in news_content_without_ticker_checked:
            financial_entities_matches = extract_financial_entities(news.content)

            if not financial_entities_matches:
                yield {
                    "news_id": news.id,
                    "entity_name": None,
                    "entity_type": None,
                    "exchange": None,
                }
            else:
                for match in financial_entities_matches:
                    yield {
                        "news_id": news.id,
                        "entity_name": match["entity_name"],
                        "entity_type": match["entity_type"],
                        "exchange": match["exchange"],
                    }


def perform_trigram_search_on_financial_entities(
    exchange_market: ExchangeSchema,
    entity_name: str,
    entity_type: Literal["STOCK_SYMBOL", "STOCK_CODE", "COMPANY_NAME"],
):
    with db_context() as db_session:
        similarity_condition = StockSymbolOrm.exchange == exchange_market
        rank = func.similarity(StockSymbolOrm.company_name, entity_name)

        if entity_type == "STOCK_SYMBOL":
            similarity_condition &= StockSymbolOrm.stock_symbol.op("%")(entity_name)
            rank = func.similarity(StockSymbolOrm.stock_symbol, entity_name)
        elif entity_type == "STOCK_CODE":
            similarity_condition &= StockSymbolOrm.stock_code.op("%")(entity_name)
            rank = func.similarity(StockSymbolOrm.stock_code, entity_name)
        elif entity_type == "COMPANY_NAME":
            similarity_condition &= StockSymbolOrm.company_name.op("%")(entity_name)
            rank = func.similarity(StockSymbolOrm.company_name, entity_name)

        result = (
            db_session.query(
                StockSymbolOrm.id,
                StockSymbolOrm.stock_symbol,
                StockSymbolOrm.company_name,
            )
            .filter(similarity_condition)
            .order_by(desc(rank))
            .first()
        )
        if result is not None:
            return {
                "stock_id": result.id,
                "stock_symbol": result.stock_symbol,
                "company_name": result.company_name,
            }
        else:
            return {"stock_id": None, "stock_symbol": None, "company_name": None}


if __name__ == "__main__":
    import pandas as pd

    news_items = extract_financial_entities_from_news_db()
    news_to_stocksymbols_items = []
    for item in news_items:
        stock_ids = perform_trigram_search_on_financial_entities(
            exchange_market=item["exchange"],
            entity_name=item["entity_name"],
            entity_type=item["entity_type"],
        )

        news_to_stocksymbols = {
            "news_id": item["news_id"],
            "stock_id": stock_ids["stock_id"],
            "exchange": item["exchange"],
            "entity_type": item["entity_type"],
            "entity_name": item["entity_name"],
            "stock_symbol": stock_ids["stock_symbol"],
            "company_name": stock_ids["company_name"],
        }
        news_to_stocksymbols_items.append(news_to_stocksymbols)

    _ = pd.DataFrame(news_to_stocksymbols_items).to_csv(
        "data/news_to_stocksymbols/nts_.csv", index=False
    )
