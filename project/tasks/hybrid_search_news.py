from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from project.db_connection import db_context

# note: pgvector '<=>' operator is used to calculate cosine similarity between two vectors


def find_news_ids(db: Session, companies_name: list[str]):
    news_ids = """
      SELECT ntss.news_id 
        FROM news_to_stock_symbol ntss
        JOIN stock_symbols ss ON ntss.stock_symbol_id = ss.id
        WHERE ss.company_name = ANY(:companies_name)
      """
    params = {"companies_name": companies_name}
    news_ids = db.execute(text(news_ids), params).scalars().all()
    return news_ids


def find_similar_news(
    db: Session,
    query_text: str,
    news_ids: tuple[int],
    match_count: int,
    rrf_k: int,
    full_text_weight: float,
    semantic_weight: float,
    decay_rate: float,
    selected_datetime: datetime,
):
    full_text_search_sql_command = """
        SELECT
          id,
          row_number() OVER (
            ORDER BY ts_rank_cd(fts, plainto_tsquery(:query_text)) ASC
          ) AS rank_ix
        FROM news
        WHERE fts @@ plainto_tsquery(:query_text) AND id = ANY(:news_ids)
        LIMIT LEAST(:match_count, 30)
      """

    vector_search_sql_command = """
        SELECT
          id,
          row_number() OVER (
            ORDER BY (embedding <=> (:query_embedding)::vector) ASC
          ) AS rank_ix
        FROM news
        WHERE embedding <=> (:query_embedding)::vector > 0.3 AND id = ANY(:news_ids)
        LIMIT LEAST(:match_count, 30)
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
        news.created_at,
        news.content,
        COALESCE(1.0 / (:rrf_k + full_text.rank_ix), 0.0) * :full_text_weight +
          COALESCE(1.0 / (:rrf_k + semantic.rank_ix), 0.0) * :semantic_weight AS score
      FROM
        full_text
        FULL OUTER JOIN semantic ON full_text.id = semantic.id
        JOIN news ON COALESCE(full_text.id, semantic.id) = news.id
      ORDER BY score DESC
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
        "news_ids": news_ids,
    }

    # Hybrid search
    from project.schemas.news_schema import NewsSearchReturn

    results = db.execute(text(hybrid_search_sql_command), params)
    hybrid_search_results = [
        NewsSearchReturn(**dict(row)) for row in results.mappings()
    ]
    return hybrid_search_results


if __name__ == "__main__":
    from project.utils.embedding_handler import get_embedding

    query_text = "genting malaysia's project"
    query_embedding = get_embedding(query_text)["data"][0]["embedding"]
    companies_name = ["GENTING MALAYSIA BERHAD", "GENTING BHD"]
    match_count = 50
    rrf_k = 50
    full_text_weight = 1
    semantic_weight = 1
    decay_rate = 1e-6
    selected_datetime = datetime.now()

    with db_context() as db_session:
        news_ids = find_news_ids(db_session, companies_name)

        hybrid_search_results = find_similar_news(
            db_session,
            query_text,
            news_ids,
            match_count,
            rrf_k,
            full_text_weight,
            semantic_weight,
            decay_rate,
            selected_datetime,
        )
        print("Hybrid news search: ", hybrid_search_results)
        print(len(hybrid_search_results))

        # Export to CSV
        keyword_search_results = [
            {
                "title": result.title,
                "created_at": result.created_at,
                "content": result.content,
                "score": result.score,
            }
            for result in hybrid_search_results
        ]

        from project.utils.csv_handler import export_list_to_csv

        _ = export_list_to_csv(
            ".backup/hybrid_search_results.csv", hybrid_search_results
        )
