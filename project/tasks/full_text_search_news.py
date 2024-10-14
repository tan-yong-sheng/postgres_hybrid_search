from sqlalchemy import func
from sqlalchemy.orm import Session

from project.db_models import NewsOrm
from project.schemas.news_schema import NewsSearchReturn


# note: need to add pydantic model for the response
def find_news_with_keywords(db: Session, query, limit=10):
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
        NewsSearchReturn(
            **{
                "title": result.title,
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
        query = "malaysia"
        keyword_search_results = find_news_with_keywords(db, query)
        print("Keyword search result: ", keyword_search_results)
