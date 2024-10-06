from typing import Literal

from sqlalchemy.sql.expression import false

from db_connection import db_context
from db_models import NewsOrm, StockSymbolOrm
from schemas import ExchangeSchema, StockCodeReturn
from utils.nlp_handler import extract_financial_entities


def extract_financial_entities_from_news_db():
    with db_context() as db_session:
        news_content_without_ticker_checked = (
            db_session.query(NewsOrm).filter(NewsOrm.is_ticker_checked == false()).all()
        )

        for news in news_content_without_ticker_checked:
            financial_entities_matches = extract_financial_entities(news.content)
            financial_entities_matches = {
                "news_id": news.id,
                "financial_entities": financial_entities_matches,
                "created_at": news.created_at,
                "title": news.title,
            }
            yield financial_entities_matches


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

        result = db_session.query(StockSymbolOrm).filter(similarity_condition).first()
        stock_code = StockCodeReturn(**result.__dict__).stock_code
        yield stock_code


if __name__ == "__main__":
    import time

    start = time.time()

    news_items = extract_financial_entities_from_news_db()
    for item in news_items:
        data = item["financial_entities"]
        print("===================================")
        for entity in data:
            extracted_data = perform_trigram_search_on_financial_entities(
                exchange_market="Bursa",
                entity_name=entity["entity_name"],
                entity_type=entity["entity_type"],
            )
            print("Stock code: ", list(extracted_data))
        print("-----------------------------------")

    end = time.time()

    print("Time taken: ", end - start, " seconds")
