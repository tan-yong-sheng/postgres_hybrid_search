import logging

from pydantic import ValidationError
from sqlalchemy.orm import Session

from db_connection import db_context
from models import StockSymbolOrm
from schemas import StockSymbolCreate

logger = logging.getLogger(__name__)


def check_existing_ticker(db: Session, stock_symbol: str):
    existing_ticker = (
        db.query(StockSymbolOrm)
        .filter(StockSymbolOrm.stock_symbol == stock_symbol)
        .first()
    )
    if existing_ticker:
        logger.info(f"The stock code: {stock_symbol} already exists")
    return existing_ticker


def insert_ticker_csv_into_db(csv_file_path: str):
    from utils.csv_handler import read_csv_file

    rows = read_csv_file(csv_file_path)
    with db_context() as db_session:
        for row in rows:
            stock_symbol = row["stock_symbol"]
            existing_stock_code = check_existing_ticker(db_session, stock_symbol)
            if not existing_stock_code:
                try:
                    stock_symbol_dict = StockSymbolCreate(**row)
                    stock_symbol_obj = StockSymbolOrm(**stock_symbol_dict.__dict__)
                    db_session.add(stock_symbol_obj)
                    db_session.commit()
                except ValidationError as e:
                    logger.error("Validation error: ", e)
                    print(e)
                    db_session.rollback()


if __name__ == "__main__":
    import os

    os.makedirs("data/symbols", exist_ok=True)

    insert_ticker_csv_into_db("data/symbols/bursa_stock_list.csv")
