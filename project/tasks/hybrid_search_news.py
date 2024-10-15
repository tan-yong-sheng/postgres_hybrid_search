from datetime import datetime

from sqlalchemy import text

from project.db_connection import engine


def find_similar_news(
    query_text,
    match_count,
    rrf_k,
    full_text_weight,
    semantic_weight,
    decay_rate,
    selected_datetime,
):
    full_text_search_sql_command = """
        SELECT
          id,
          row_number() OVER (
            ORDER BY ts_rank_cd(fts, plainto_tsquery(:query_text)) * 5 + 
            (1 - :decay_rate) ^ EXTRACT(EPOCH FROM (:selected_datetime - created_at) / 43200) DESC
          ) AS rank_ix
        FROM news
        WHERE fts @@ plainto_tsquery(:query_text)
        ORDER BY rank_ix
        LIMIT LEAST(:match_count, 30) * 2
      """

    vector_search_sql_command = """
        SELECT
          id,
          row_number() OVER (
            ORDER BY (embedding <=> (:query_embedding)::vector) * 5 + 
            (1 - :decay_rate) ^ EXTRACT(EPOCH FROM (:selected_datetime - created_at) / 43200) DESC
          ) AS rank_ix
        FROM news
        ORDER BY rank_ix
        LIMIT LEAST(:match_count, 30) * 2
      """

    hybrid_search_sql_command = f"""
      WITH full_text AS (
        {full_text_search_sql_command}
      ),
      semantic AS (
        {vector_search_sql_command}
      )
      SELECT
        news.title,
        news.content,
        COALESCE(1.0 / (:rrf_k + full_text.rank_ix), 0.0) * :full_text_weight +
          COALESCE(1.0 / (:rrf_k + semantic.rank_ix), 0.0) * :semantic_weight AS score
      FROM
        full_text
        FULL OUTER JOIN semantic ON full_text.id = semantic.id
        JOIN news ON COALESCE(full_text.id, semantic.id) = news.id
      ORDER BY
        score DESC
      LIMIT LEAST(:match_count, 30)
      """

    params = {
        "query_text": query_text,
        "query_embedding": query_embedding,
        "match_count": match_count,
        "rrf_k": rrf_k,
        "full_text_weight": full_text_weight,
        "semantic_weight": semantic_weight,
        "decay_rate": decay_rate,
        "selected_datetime": selected_datetime,
    }

    with engine.connect() as conn:
        # Hybrid search
        from project.schemas.news_schema import NewsSearchReturn

        results = conn.execute(text(hybrid_search_sql_command), params)
        hybrid_search_results = [
            NewsSearchReturn(**dict(row)) for row in results.mappings()
        ]
        return hybrid_search_results


if __name__ == "__main__":
    from project.utils.embedding_handler import get_embedding

    query_text = "genting malaysia's project"
    query_embedding = get_embedding(query_text)["data"][0]["embedding"]
    match_count = 50
    rrf_k = 50
    full_text_weight = 1
    semantic_weight = 1
    decay_rate = 1e-6
    selected_datetime = datetime.now()

    hybrid_search_results = find_similar_news(
        query_text,
        match_count,
        rrf_k,
        full_text_weight,
        semantic_weight,
        decay_rate,
        selected_datetime,
    )
    print("Hybrid news search: ", hybrid_search_results)
