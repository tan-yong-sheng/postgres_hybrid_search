from datetime import datetime

from sqlalchemy import text

from project.db_connection import engine
from project.utils.embedding_handler import get_embedding

query_text = "what happens to genting malaysia"
query_embedding = get_embedding(query_text)
match_count = 50
rrf_k = 50
full_text_weight = 1
semantic_weight = 1
decay_rate = 1e-6  # Increased for better precision
selected_datetime = datetime.strptime("2024-09-30 11:10:41", "%Y-%m-%d %H:%M:%S")


hybrid_search_sql_command = text("""
WITH full_text AS (
  SELECT
    id,
    row_number() OVER (
      ORDER BY ts_rank_cd(fts, websearch_to_tsquery(:query_text)) * 5 + 
      (1 - :decay_rate) ^ EXTRACT(EPOCH FROM (:selected_datetime - created) / 43200) DESC
    ) AS rank_ix
  FROM news
  WHERE fts @@ websearch_to_tsquery(:query_text)
  ORDER BY rank_ix
  LIMIT LEAST(:match_count, 30) * 2
),
semantic AS (
  SELECT
    id,
    row_number() OVER (
      ORDER BY (embedding <=> :query_embedding) * 5 + 
      (1 - :decay_rate) ^ EXTRACT(EPOCH FROM (:selected_datetime - created) / 43200) DESC
    ) AS rank_ix
  FROM news
  ORDER BY rank_ix
  LIMIT LEAST(:match_count, 30) * 2
)
SELECT
  news.title,
  news.content
FROM
  full_text
  FULL OUTER JOIN semantic ON full_text.id = semantic.id
  JOIN news ON COALESCE(full_text.id, semantic.id) = news.id
ORDER BY
  COALESCE(1.0 / (:rrf_k + full_text.rank_ix), 0.0) * :full_text_weight +
  COALESCE(1.0 / (:rrf_k + semantic.rank_ix), 0.0) * :semantic_weight DESC
LIMIT LEAST(:match_count, 30)
""")

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
    results = conn.execute(hybrid_search_sql_command, **params)
    for row in results:
        print(row)
