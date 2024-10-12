import os

import openai
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.sql.expression import null
from tqdm import tqdm

from project.db_connection import db_context
from project.db_models import NewsOrm

_ = load_dotenv(find_dotenv())

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
CLOUDFLARE_GATEWAY_ID = os.getenv("CLOUDFLARE_GATEWAY_ID")

openai_client = openai.OpenAI(
    api_key=CLOUDFLARE_API_KEY,
    base_url=f"https://gateway.ai.cloudflare.com/v1/{CLOUDFLARE_ACCOUNT_ID}/{CLOUDFLARE_GATEWAY_ID}/workers-ai/v1/",
)


def check_empty_embeddings_in_news_db():
    with db_context() as db_session:
        # check if the database have any rows with empty embeddings
        results = db_session.query(NewsOrm).filter(NewsOrm.embedding == null()).all()
        return results


def get_embedding(input: str):
    response = openai_client.embeddings.create(
        model="@cf/baai/bge-small-en-v1.5", input=input
    )
    return response.model_dump()


def update_embeddings_by_news_id(embedding_data: list[float]):
    news_with_empty_embeddings = check_empty_embeddings_in_news_db()
    ## update news record with created embeddings
    if news_with_empty_embeddings:
        with db_context() as db_session:
            for news in tqdm(news_with_empty_embeddings):
                print(news.title)
                embedding = get_embedding(
                    input=f"<title>{news.title}</title><content>{news.content}</content>",
                )

                setattr(news, "embedding", embedding)
                db_session.add(news)
                db_session.commit()


if __name__ == "__main__":
    _ = update_embeddings_by_news_id(...)
