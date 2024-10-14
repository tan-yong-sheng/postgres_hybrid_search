
from sqlalchemy.sql.expression import null
from tqdm import tqdm

from project.db_connection import db_context
from project.db_models import NewsOrm
from project.utils.embedding_handler import get_embedding

def check_empty_embeddings_in_news_db():
    with db_context() as db_session:
        # check if the database have any rows with empty embeddings
        results = db_session.query(NewsOrm).filter(NewsOrm.embedding == null()).all()
        return results

def insert_embeddings_into_news_db():
    news_with_empty_embeddings = check_empty_embeddings_in_news_db()
    ## update news record with created embeddings
    if news_with_empty_embeddings:
        with db_context() as db_session:
            for news in tqdm(news_with_empty_embeddings):
                embedding_data = get_embedding(
                    input=f"<title>{news.title}</title><content>{news.content}</content>",
                )
                # Extract the actual embedding vector from the response
                embedding = embedding_data["data"][0]["embedding"]
                # Update the news db with the embedding vector
                news.embedding = embedding
                # remain the other fields
                for keys, values in news.__dict__.items():
                    if keys != "embedding":
                        setattr(news, keys, values)
                db_session.add(news)
                db_session.commit()


if __name__ == "__main__":
    _ = insert_embeddings_into_news_db()
