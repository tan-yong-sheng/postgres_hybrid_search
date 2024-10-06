from sqlalchemy.sql.expression import false

from db_connection import db_context
from db_models import NewsOrm, StockSymbolOrm
from utils.nlp_handler import extract_financial_entities


def extract_financial_entities_from_news_db():
    with db_context() as db_session:
        news_content_without_ticker_checked = (
            db_session.query(NewsOrm).filter(NewsOrm.is_ticker_checked == false()).all()
        )

        for news in news_content_without_ticker_checked:
            financial_entities_matches = extract_financial_entities(news.content)
            print("Match for spacy: ", financial_entities_matches)
            print("News id: ", news.id)  # write to csv?
            print("-------------")


def perform_trigram_search_on_financial_entities(
    exchange_market: str, financial_entities: dict
):
    with db_context() as db_session:
        results = db_session.query(StockSymbolOrm).all()
        for result in results:
            yield result.__dict__


if __name__ == "__main__":
    _ = extract_financial_entities_from_news_db()

    # matches = perform_trigram_search_on_financial_entities("Bursa", {})
    # for match in matches:
    #    print(match)
