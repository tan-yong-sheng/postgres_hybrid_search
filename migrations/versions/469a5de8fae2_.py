"""empty message

Revision ID: 469a5de8fae2
Revises:
Create Date: 2024-10-20 02:47:16.358378

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "469a5de8fae2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "hnsw_idx_news_content_trgm",
        table_name="news",
        postgresql_with={"m": "16", "ef_construction": "64"},
        postgresql_using="hnsw",
    )
    op.create_index(
        "hnsw_idx_news_content_embedding",
        "news",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "hnsw_idx_news_content_embedding",
        table_name="news",
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_index(
        "hnsw_idx_news_content_trgm",
        "news",
        ["embedding"],
        unique=False,
        postgresql_with={"m": "16", "ef_construction": "64"},
        postgresql_using="hnsw",
    )
    # ### end Alembic commands ###
