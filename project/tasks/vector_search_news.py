from project.db_models import NewsOrm


# note: need to add pydantic model for the response
def find_similar_embeddings(query_embedding, limit=5):
    # Note: need to double check its sql query...
    # Note: the lower (or smaller) the distance metrics, the more relevance the embedding is...
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
        {
            "title": result.title,
            "content": result.content,
            "score": 1 - result.distance,
        }
        for result in results
    ]


if __name__ == "__main__":
    from project.db_connection import db_context

    with db_context() as db:
        # Embedding search
        from project.schemas.news_schema import NewsSearchReturn
        from project.utils.embedding_handler import get_embedding

        query = "Genting malaysia's project"
        query_embedding = get_embedding(input=query)["data"][0]["embedding"]
        semantic_search_results = find_similar_embeddings(query_embedding)
        semantic_search_results = [
            NewsSearchReturn(**result) for result in semantic_search_results
        ]
        print("Semantic search result: ", semantic_search_results)
