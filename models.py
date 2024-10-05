from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    CheckConstraint,
    Column,
    Computed,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.types import DateTime, Integer, String

from db_connection import Base


# Define the stock_symbol table
class StockSymbolOrm(Base):
    __tablename__ = "stock_symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_symbol = Column(String)
    company_name = Column(String)
    stock_code = Column(String)
    sector = Column(String)
    subsector = Column(String)
    mkt = Column(String)
    exchange = Column(String)
    company_description = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("stock_symbol", "exchange", name="uq_stock_symbol_exchange"),
        Index(
            "idx_stock_symbol_trgm",
            "stock_symbol",
            postgresql_using="gist",
            postgresql_ops={"stock_symbol": "gist_trgm_ops(siglen=256)"},
        ),
        Index(
            "idx_stock_code_trgm",
            "stock_code",  # index for trigram search on multiple fields
            postgresql_using="gist",
            postgresql_ops={"stock_code": "gist_trgm_ops(siglen=256)"},
        ),
        Index(
            "idx_company_name_trgm",
            "company_name",  # index for trigram search on multiple fields
            postgresql_using="gist",
            postgresql_ops={"company_name": "gist_trgm_ops(siglen=256)"},
        ),
    )


class NewsOrm(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    title = Column(String(300), nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(Vector(384), nullable=True)
    fts = Column(
        TSVECTOR(),
        Computed("to_tsvector('english', content)", persisted=True),
    )

    __table_args__ = (
        UniqueConstraint("created_at", "title", name="uq_news_createdat_title"),
        CheckConstraint("LENGTH(title)>0", name="check_title_length"),
        CheckConstraint("LENGTH(content)>0", name="check_content_length"),
        Index(
            "hnsw_idx_news_chunks_trgm",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        # Create index for keyword-based search (or sparse vector search), executed via `tsvector`
        Index("ix_newschunk_fts___ts_vector__", fts, postgresql_using="gin"),
    )


class NewsToStockSymbol(Base):
    __tablename__ = "news_to_stock_symbol"

    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="cascade"), nullable=False)
    stock_symbol_id = Column(
        Integer, ForeignKey("stock_symbols.id", ondelete="cascade"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("news_id", "stock_symbol_id", name="uq_news_stock_symbol"),
    )


if __name__ == "__main__":
    # Create the tables in database
    from db_connection import engine

    Base.metadata.create_all(engine)
