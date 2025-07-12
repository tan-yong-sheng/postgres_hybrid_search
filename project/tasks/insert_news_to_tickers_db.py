import argparse
import logging
from datetime import datetime

from pydantic import ValidationError
from sqlalchemy.orm import Session

from project.db_connection import db_context
from project.db_models import NewsOrm, NewsToStockSymbolOrm
from project.schemas.news_to_stocksymbol_schema import NewsToStockSymbolCreate

logger = logging.getLogger(__name__)


def check_existing_news_to_stock_symbol(
    db_session: Session,
    news_to_stock_symbol: dict,
) -> NewsToStockSymbolOrm:
    """Check if the uploaded data has the same news record, with same stock_symbol_id"""
    try:
        news_to_stock_symbol_obj = NewsToStockSymbolCreate(**news_to_stock_symbol)
        existing_news_to_stock_symbol = (
            db_session.query(NewsToStockSymbolOrm)
            .filter(
                NewsToStockSymbolOrm.news_id == news_to_stock_symbol_obj.news_id,
                NewsToStockSymbolOrm.stock_symbol_id
                == news_to_stock_symbol_obj.stock_symbol_id,
            )
            .first()
        )
        return existing_news_to_stock_symbol
    except ValidationError as e:
        logger.debug(
            f"{e} : Either news_id or stock_symbol_id is missing in the dataset"
        )
        return None


def insert_news_to_stock_symbol(csv_file_path: str) -> list[int]:
    """Insert news id, stock id from csv into the `news_to_stock_symbol` table"""
    from project.utils.csv_handler import read_csv_file

    rows = read_csv_file(csv_file_path)
    news_id_list = []
    with db_context() as db_session:
        for row in rows:
            try:
                existing_news_to_stock_symbol = check_existing_news_to_stock_symbol(
                    db_session, row
                )  # ensure there is no duplicate news entry

                if not existing_news_to_stock_symbol:
                    news_to_stock_symbol_dict = NewsToStockSymbolCreate(**row)
                    news_to_stock_symbol_obj = NewsToStockSymbolOrm(
                        **news_to_stock_symbol_dict.__dict__
                    )
                    db_session.add(news_to_stock_symbol_obj)
                    db_session.commit()
                    # used .refresh() method when you want to get up-to-date object
                    db_session.refresh(news_to_stock_symbol_obj)

                    news_id_list.append(news_to_stock_symbol_obj.news_id)
            except ValidationError as e:
                logger.info(
                    f"{e}: Either news_id or stock_symbol_id is missing in the dataset"
                )
        return news_id_list


def update_news_is_ticker_checked(news_id: int):
    """Update the `is_ticker_checked` column to True for the `news` table"""

    with db_context() as db_session:
        news = db_session.query(NewsOrm).filter(NewsOrm.id == news_id).first()
        news.is_ticker_checked = True
        db_session.commit()


if __name__ == "__main__":
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
        news_id_list_with_successful_update = insert_news_to_stock_symbol(
            f"data/news_to_stocksymbols/nts_{end}.csv"
        )
        logger.info(
            f"Inserting news to stock symbol from csv file: data/news_to_stocksymbols/nts_{end}.csv"
        )

        # Update the `is_ticker_checked` column to True for the `news` table
        if news_id_list_with_successful_update:
            for news_id in news_id_list_with_successful_update:
                _ = update_news_is_ticker_checked(news_id)
                logger.info(
                    f"updating news database for updating tickers for news_id: {news_id}"
                )
