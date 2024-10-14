from sqlalchemy import func
from sqlalchemy.orm import Session

from project.db_models import NewsOrm


def find_similar_keywords(db: Session, query, limit=10):
    results = (
        db.query(
            NewsOrm.title,
            NewsOrm.content,
            func.ts_rank(
                NewsOrm.fts, func.websearch_to_tsquery("english", query)
            ).label("rank"),
        )
        .filter(NewsOrm.fts.match(query))
        .order_by(
            func.ts_rank(
                NewsOrm.fts, func.websearch_to_tsquery("english", query)
            ).desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "title": result.title,
            "content": result.content,
            "score": result.rank,
        }
        for result in results
    ]


def find_similar_embeddings(query_embedding, limit=5):
    # Note: need to double check its sql query...
    # Note: the lower (or smaller) the distance metrics, the more relevance the embedding is...
    similarity_threshold = 0.7
    query = (
        db.query(
            NewsOrm,
            NewsOrm.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .filter(
            NewsOrm.embedding.cosine_distance(query_embedding) < similarity_threshold
        )
        .order_by("distance")
        .limit(limit)
        .all()
    )
    return [
        {"title": q[0].title, "content": q[0].content, "score": 1 - q[1]} for q in query
    ]


if __name__ == "__main__":
    from project.db_connection import db_context

    with db_context() as db:
        # part 1: keyword search
        query = "Bursa Malaysia"
        keyword_search_results = find_similar_keywords(db, query)
        print("Keyword search result: ", keyword_search_results)

        # part 2: embedding search
        print("----------------------------")
        # need to move this get_embedding() function to utils/?
        from project.tasks.insert_news_embedding_db import get_embedding

        query_embedding = get_embedding(input=query)
        semantic_search_results = find_similar_embeddings(query_embedding)
        print(
            "Semantic search result: ", semantic_search_results
        )  # BUG: not working yet...
