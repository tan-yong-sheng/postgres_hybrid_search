import sys
import os
from datetime import datetime
from typing import Optional

from fastmcp.server import FastMCP
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from project import db_context, get_embedding

# Pydantic models for MCP responses
class NewsSearchResult(BaseModel):
    id: str

class NewsSearchResultPage(BaseModel):
    results: list[NewsSearchResult]
    total_count: int
    query: str

class NewsDetail(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    score: Optional[float] = None
    metadata: Optional[dict] = None

# Database functions (adapted from original)
def find_similar_news(
    db: Session,
    query_text: str,
    match_count: int,
    rrf_k: int,
    full_text_weight: float,
    semantic_weight: float,
    query_embedding: list[float],
):
    """Perform hybrid search on news articles"""
    full_text_search_sql_command = """
        SELECT
          id,
          row_number() OVER (
            ORDER BY ts_rank_cd(fts, plainto_tsquery(:query_text)) DESC
          ) AS rank_ix
        FROM news
        WHERE fts @@ plainto_tsquery(:query_text)
        LIMIT LEAST(:match_count, 30)
      """

    vector_search_sql_command = """
        SELECT
          id,
          row_number() OVER (
            ORDER BY (embedding <=> (:query_embedding)::vector) ASC
          ) AS rank_ix
        FROM news
        WHERE embedding <=> (:query_embedding)::vector > 0.3
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
        news.id,
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
    }

    results = db.execute(text(hybrid_search_sql_command), params)
    return [dict(row) for row in results.mappings()]

def create_server():
    """Create the FastMCP server for hybrid news search"""
    mcp = FastMCP(
        name="Hybrid News Search MCP", 
        host="0.0.0.0",
        instructions="Search and retrieve news articles using hybrid search (full-text + semantic)"
    )

    @mcp.tool()
    async def search(
        query: str,
        match_count: int = 10,
        rrf_k: int = 50,
        full_text_weight: float = 0.2,
        semantic_weight: float = 0.8,
    ) -> NewsSearchResultPage:
        """
        Search for news articles using hybrid search (full-text + semantic).
        
        Args:
            query: The search query text
            match_count: Maximum number of results to return (default: 10)
            rrf_k: RRF (Reciprocal Rank Fusion) parameter (default: 50)
            full_text_weight: Weight for full-text search component (default: 1.0)
            semantic_weight: Weight for semantic search component (default: 1.0)
            
        Returns:
            NewsSearchResultPage containing search results and metadata
        """
        try:
            # Get embedding for the query
            query_embedding = get_embedding(query)["data"][0]["embedding"]
            
            with db_context() as db_session:
                # Perform hybrid search
                search_results = find_similar_news(
                    db_session,
                    query,
                    match_count,
                    rrf_k,
                    full_text_weight,
                    semantic_weight,
                    query_embedding,
                )
                
                # Convert to Pydantic models
                results = [
                    NewsSearchResult(
                        id=str(result["id"])
                    )
                    for result in search_results
                ]
                
                return NewsSearchResultPage(
                    results=results,
                    total_count=len(results),
                    query=query
                )
                
        except Exception as e:
            raise ValueError(f"Search failed: {str(e)}")

    @mcp.tool()
    async def fetch(news_id: str) -> NewsDetail:
        """
        Fetch a specific news article by ID.
        
        Args:
            news_id: The ID of the news article to fetch
            
        Returns:
            NewsDetail containing the full article details
        """
        try:
            with db_context() as db_session:
                fetch_sql = """
                    SELECT id, title, content, created_at
                    FROM news
                    WHERE id = :news_id
                """
                
                result = db_session.execute(
                    text(fetch_sql), 
                    {"news_id": int(news_id)}
                ).mappings().first()
                
                if not result:
                    raise ValueError(f"News article with ID {news_id} not found")
                
                return NewsDetail(
                    id=str(result["id"]),
                    title=result["title"],
                    content=result["content"],
                    created_at=result["created_at"]
                )
                
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Fetch failed: {str(e)}")

    return mcp

if __name__ == "__main__":
    create_server().run(transport="sse")