from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import desc

from project.db_models import NewsOrm, NewsToStockSymbol, StockSymbolOrm
from project.schemas.news_schema import NewsSearchReturn


def find_news_with_similar_embeddings(
    db: Session, query_embedding: list[float], companies_name: list[str], limit: int = 5
):
    similarity_threshold = 0.7
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

        query = "future projection"
        companies = ["GENTING BHD", "GENTING MALAYSIA BERHAD"]
        query_embedding = get_embedding(input=query)["data"][0]["embedding"]
        semantic_search_results = find_news_with_similar_embeddings(
            db, query_embedding, companies_name=companies
        )
        print("Semantic search result: ", semantic_search_results)
        print("Semantic search result: ", semantic_search_results)
