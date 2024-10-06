from sqlalchemy import func
from sqlalchemy.sql.expression import desc

from db_connection import db_context
from db_models import StockSymbolOrm
from schemas import StockSymbolReturn

search_term = "genting malaysia"
exchange_market = "Bursa"
prefix = search_term[:2].upper()

with db_context() as session:
    # Conditions for similarity matching
    # Note: similarity functions do not use the index when doing filters in the WHERE clause
    similarity_condition = (
        (
            (func.left(StockSymbolOrm.stock_code, 2) == prefix)
            | (func.left(StockSymbolOrm.stock_symbol, 2) == prefix)
            | (func.left(StockSymbolOrm.company_name, 2) == prefix)
        )
        & (
            (func.similarity(StockSymbolOrm.stock_code, search_term) > 0.2)
            | (func.similarity(StockSymbolOrm.stock_symbol, search_term) > 0.2)
            | (func.similarity(StockSymbolOrm.company_name, search_term) > 0.3)
        )
        & (StockSymbolOrm.exchange == exchange_market)
    )

    # Rank score based on average similarity
    rank_score = (
        func.similarity(StockSymbolOrm.stock_code, search_term)
        + func.similarity(StockSymbolOrm.stock_symbol, search_term)
        + func.similarity(StockSymbolOrm.company_name, search_term) * 1.1
    )

    # Perform trigram search based on the conditions defined above
    results = (
        session.query(StockSymbolOrm)
        .filter(similarity_condition)
        .order_by(desc(rank_score))
        .all()
    )

    results = [StockSymbolReturn(**result.__dict__) for result in results]
    print("Results: ", results)
