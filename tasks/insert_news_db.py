import logging

from pydantic import ValidationError
from sqlalchemy.orm import Session

from db_connection import db_context
from models import NewsOrm
from schemas import NewsCreate

logger = logging.getLogger(__name__)


def check_existing_news(db: Session, news: dict):
    existing_news = (
        db.query(NewsOrm)
        .filter(
            (NewsOrm.title == news["title"])
            & (NewsOrm.created_at == news["created_at"])
        )
        .first()
    )
    return existing_news


def insert_news_into_db(csv_file_path: str):
    from utils.csv_handler import read_csv_file

    rows = read_csv_file(csv_file_path)
    with db_context() as db_session:
        for row in rows:
            print(row)
            news_data = NewsCreate(**row)
            existing_news = check_existing_news(
                db_session, news_data
            )  # ensure there is no duplicate news entry
            if not existing_news:
                try:
                    db_session.add(news_data)
                    db_session.commit()
                    db_session.refresh(news_data)
                except ValidationError as e:
                    logger.error("Validation error: ", e)


if __name__ == "__main__":
    insert_news_into_db("data/news/news_2022-01-01 23:59:59.csv")

    