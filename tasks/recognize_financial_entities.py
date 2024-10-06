from typing import Literal

from sqlalchemy.sql.expression import desc, false

from db_connection import db_context
from db_models import NewsOrm, StockSymbolOrm
from schemas import ExchangeSchema
from utils.nlp_handler import extract_financial_entities


def extract_financial_entities_from_news_db():
    with db_context() as db_session:
        news_content_without_ticker_checked = (
            db_session.query(NewsOrm).filter(NewsOrm.is_ticker_checked == false()).all()
        )

        for news in news_content_without_ticker_checked:
            financial_entities_matches = extract_financial_entities(news.content)

            if not financial_entities_matches:
                yield {
                    "news_id": news.id,
                    "entity_name": None,
                    "entity_type": None,
                }
            else:
                for match in financial_entities_matches:
                    yield {
                        "news_id": news.id,
                        "entity_name": match["entity_name"],
                        "entity_type": match["entity_type"],
                    }


def perform_trigram_search_on_financial_entities(
    exchange_market: ExchangeSchema,
    entity_name: str,
    entity_type: Literal["STOCK_SYMBOL", "STOCK_CODE", "COMPANY_NAME"],
):
    with db_context() as db_session:
        similarity_condition = StockSymbolOrm.exchange == exchange_market
        if entity_type == "STOCK_SYMBOL":
            similarity_condition &= StockSymbolOrm.stock_symbol.op("%")(entity_name)
        elif entity_type == "STOCK_CODE":
            similarity_condition &= StockSymbolOrm.stock_code.op("%")(entity_name)
        elif entity_type == "COMPANY_NAME":
            similarity_condition &= StockSymbolOrm.company_name.op("%")(entity_name)

        result = (
            db_session.query(StockSymbolOrm.id)
            .filter(similarity_condition)
            .order_by(desc(similarity_condition))
            .first()
        )
        if result is not None:
            yield {"stock_id": result.id}
        else:
            yield {"stock_id": None}


if __name__ == "__main__":
    news_items = extract_financial_entities_from_news_db()

    for item in news_items:
        stock_ids = perform_trigram_search_on_financial_entities(
            exchange_market="Bursa",
            entity_name=item["entity_name"],
            entity_type=item["entity_type"],
        )

        print(
            {
                "news_id": item["news_id"],
                "stock_id": [stock_id["stock_id"] for stock_id in stock_ids][0],
            }
        )
