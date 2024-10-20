from sqlalchemy import func
from sqlalchemy.orm import Session

from project.db_models import NewsOrm, NewsToStockSymbol, StockSymbolOrm
from project.schemas.news_schema import NewsSearchReturn


# note: need to add pydantic model for the response
def find_news_with_keywords(
    db: Session, query: str, companies_name: list[str], limit: int = 10
):
    stock_ids = [
        stock_id[0]
        for stock_id in (
            db.query(StockSymbolOrm.id)
            .filter(StockSymbolOrm.company_name.in_(companies_name))
            .all()
        )
    ]
    news_ids = [
        news_id[0]
        for news_id in (
            db.query(NewsToStockSymbol.news_id)
            .filter(NewsToStockSymbol.stock_symbol_id.in_(stock_ids))
            .all()
        )
    ]

    results = (
        db.query(
            NewsOrm.title,
            NewsOrm.created_at,
            NewsOrm.content,
            func.ts_rank(NewsOrm.fts, func.plainto_tsquery("english", query)).label(
                "rank"
            ),
        )
        .filter(NewsOrm.fts.match(query) & NewsOrm.id.in_(news_ids))
        .order_by(
            func.ts_rank(NewsOrm.fts, func.plainto_tsquery("english", query)).desc()
        )
        .limit(limit)
        .all()
    )

    return [
        NewsSearchReturn(
            **{
                "title": result.title,
                "created_at": result.created_at,
                "content": result.content,
                "score": result.rank,
            }
        )
        for result in results
    ]


if __name__ == "__main__":
    from project.db_connection import db_context

    with db_context() as db:
        # Keyword search
        query = "project"
        companies_name = ["GENTING MALAYSIA BERHAD", "GENTING BHD"]
        keyword_search_results = find_news_with_keywords(db, query, companies_name)
        print("Keyword search result: ", keyword_search_results)

        # Export to CSV
        keyword_search_results = [
            {
                "title": result.title,
                "created_at": result.created_at,
                "content": result.content,
                "score": result.score,
            }
            for result in keyword_search_results
        ]

        from project.utils.csv_handler import export_list_to_csv

        _ = export_list_to_csv(
            ".backup/keyword_search_results.csv", keyword_search_results
        )