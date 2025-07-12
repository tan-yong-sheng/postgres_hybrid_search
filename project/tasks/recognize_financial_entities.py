import argparse
import logging
from datetime import datetime
from typing import Iterable, Literal

from sqlalchemy.sql.expression import desc, func

from project.db_connection import db_context
from project.db_models import NewsOrm, StockSymbolOrm
from project.utils.nlp_stock_handler import extract_financial_entities

logger = logging.getLogger(__name__)


def query_news_content(db_session, start_date: datetime, end_date: datetime):
    return (
        db_session.query(NewsOrm)
        .filter(
            NewsOrm.created_at >= start_date,
            NewsOrm.created_at <= end_date,
        )
        .all()
    )


def extract_financial_entities_from_news_db(
    start_date: datetime, end_date: datetime
) -> Iterable[dict]:
    with db_context() as db_session:
        news_content_without_ticker_checked = query_news_content(
            db_session, start_date, end_date
        )

        for news in news_content_without_ticker_checked:
            financial_entities_matches = extract_financial_entities(news.content)
            if financial_entities_matches:
                for match in financial_entities_matches:
                    yield {
                        "news_id": news.id,
                        "entity_name": match["entity_name"],
                        "entity_type": match["entity_type"],
                        "exchange": match["exchange"],
                    }


def perform_trigram_search_on_financial_entities(
    exchange_market: Literal["Bursa", "SGX"],
    entity_name: str,
    entity_type: Literal["STOCK_SYMBOL", "STOCK_CODE", "COMPANY_NAME"],
) -> dict:
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
                "stock_symbol_id": result.id,
                "stock_symbol": result.stock_symbol,
                "company_name": result.company_name,
            }
        else:
            return {"stock_symbol_id": None, "stock_symbol": None, "company_name": None}


if __name__ == "__main__":
    import os
    
    os.makedirs("data/news_to_stocksymbols", exist_ok=True)
    
    from project.utils.date_handler import generate_date_ranges

    parser = argparse.ArgumentParser(description="Scrape KLSE news between two datetime ranges.")
    parser.add_argument(
        "--start-date", required=True, help="Start date in format YYYY-MM-DD HH:MM:SS"
    )
    parser.add_argument(
        "--end-date", required=True, help="End date in format YYYY-MM-DD HH:MM:SS"
    )

    args = parser.parse_args()
    
    # Define the overall date range
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d %H:%M:%S")

    for start, end in generate_date_ranges(
        start_date, end_date
    ):
        news_items = extract_financial_entities_from_news_db(start, end)

        news_to_stocksymbols_items = []
        for item in news_items:
            stock_symbol_ids = perform_trigram_search_on_financial_entities(
                exchange_market=item["exchange"],
                entity_name=item["entity_name"],
                entity_type=item["entity_type"],
            )

            news_to_stocksymbols = {
                "news_id": item["news_id"],
                "stock_symbol_id": stock_symbol_ids["stock_symbol_id"],
                "exchange": item["exchange"],
                "entity_type": item["entity_type"],
                "entity_name": item["entity_name"],
                "stock_symbol": stock_symbol_ids["stock_symbol"],
                "company_name": stock_symbol_ids["company_name"],
            }
            news_to_stocksymbols_items.append(news_to_stocksymbols)

        from project.utils.csv_handler import export_list_to_csv

        _ = export_list_to_csv(
            f"data/news_to_stocksymbols/nts_{end}.csv",
            news_to_stocksymbols_items,
        )
