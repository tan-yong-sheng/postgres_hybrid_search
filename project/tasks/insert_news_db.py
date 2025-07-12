import argparse
import logging
from datetime import datetime

from pydantic import ValidationError
from sqlalchemy.orm import Session

from project.db_connection import db_context
from project.db_models import NewsOrm
from project.schemas.news_schema import NewsCreate

logger = logging.getLogger(__name__)


def check_existing_news(db: Session, news: dict) -> NewsOrm:
    news_obj = NewsCreate(**news)
    existing_news = (
        db.query(NewsOrm)
        .filter(
            (NewsOrm.title == news_obj.title)
            & (NewsOrm.created_at == news_obj.created_at)
        )
        .first()
    )
    return existing_news


def insert_news_into_db(csv_file_path: str):
    from project.utils.csv_handler import read_csv_file

    rows = read_csv_file(csv_file_path)
    if not rows:
        logger.debug(f"No data found in the file: {csv_file_path}")
        return

    with db_context() as db_session:
        for row in rows:
            existing_news = check_existing_news(
                db_session, row
            )  # ensure there is no duplicate news entry
            if not existing_news:
                try:
                    news_data_dict = NewsCreate(**row)
                    news_data_obj = NewsOrm(**news_data_dict.__dict__)
                    db_session.add(news_data_obj)
                    db_session.commit()

                except ValidationError as e:
                    logger.debug("Validation error: ", e)


if __name__ == "__main__":
    from project.utils.date_handler import generate_date_ranges

    parser = argparse.ArgumentParser(description="Insert KLSE news into Database between two datetime ranges.")
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

    # Loop over each date range and scrape news data
    for start, end in generate_date_ranges(
        start_date, end_date
    ):
        print(f"Inserting news from csv file: data/news/news_{end}.csv")
        _ = insert_news_into_db(f"data/news/news_{end}.csv")
