from project.db_models import NewsOrm
from project.schemas.news_schema import NewsSearchReturn


def find_news_with_similar_embeddings(query_embedding, limit=5):
    similarity_threshold = 0.7
    results = (
        db.query(
            NewsOrm.title,
            NewsOrm.content,
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
        NewsSearchReturn(
            **{
                "title": result.title,
                "content": result.content,
                "score": 1 - result.distance,
            }
        )
        for result in results
    ]


if __name__ == "__main__":
    from project.db_connection import db_context

    with db_context() as db:
        # Embedding search
        from project.utils.embedding_handler import get_embedding

        query = "Genting malaysia's project"
        query_embedding = get_embedding(input=query)["data"][0]["embedding"]
        semantic_search_results = find_news_with_similar_embeddings(query_embedding)
        print("Semantic search result: ", semantic_search_results)
