from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import desc

from project.db_models import NewsOrm, NewsToStockSymbolOrm, StockSymbolOrm
from project.schemas.news_schema import NewsSearchReturn


def find_news_with_similar_embeddings(
    db: Session,
    query_embedding: list[float],
    companies_name: list[str],
    limit: int = 30,
):
    similarity_threshold = 0.7
    stock_symbol_ids = [
        stock_symbol_id[0]
        for stock_symbol_id in (
            db.query(StockSymbolOrm.id)
            .filter(StockSymbolOrm.company_name.in_(companies_name))
            .all()
        )
    ]
    news_ids = [
        news_id[0]
        for news_id in (
            db.query(NewsToStockSymbolOrm.news_id)
            .filter(NewsToStockSymbolOrm.stock_symbol_id.in_(stock_symbol_ids))
            .all()
        )
    ]

    results = (
        db.query(
            NewsOrm.title,
            NewsOrm.created_at,
            NewsOrm.content,
            (1 - NewsOrm.embedding.cosine_distance(query_embedding)).label("score"),
        )
        .filter(
            NewsOrm.embedding.cosine_distance(query_embedding) < similarity_threshold
        )
        .filter(NewsOrm.id.in_(news_ids))
        .order_by(desc("score"))
        .limit(limit)
        .all()
    )
    return [
        NewsSearchReturn(
            **{
                "title": result.title,
                "created_at": result.created_at,
                "content": result.content,
                "score": result.score,
            }
        )
        for result in results
    ]


if __name__ == "__main__":
    from project.db_connection import db_context

    with db_context() as db:
        # Embedding search
        from project.utils.embedding_handler import get_embedding

        query = "project"
        companies = ["GENTING MALAYSIA BERHAD", "GENTING BHD"]
        query_embedding = get_embedding(input=query)["data"][0]["embedding"]
        semantic_search_results = find_news_with_similar_embeddings(
            db, query_embedding, companies_name=companies
        )
        print("Semantic search result: ", semantic_search_results)

        # Export to CSV
        semantic_search_results = [
            {
                "title": result.title,
                "created_at": result.created_at,
                "content": result.content,
                "score": result.score,
            }
            for result in semantic_search_results
        ]

        from project.utils.csv_handler import export_list_to_csv

        _ = export_list_to_csv(
            ".backup/semantic_search_results.csv", semantic_search_results
        )
