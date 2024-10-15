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


def insert_embeddings_into_news_db(news_items):
    ## update news record with created embeddings
    with db_context() as db_session:
        for news in tqdm(news_items):
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
    ## single thread process to insert embeddings to news db...
    ## we comment this out because we want to use multi-thread process if there is a lot of text data to be processed...
    # news_contents = check_empty_embeddings_in_news_db()
    # _ = insert_embeddings_into_news_db(news_contents)

    # multi-thread process to insert embeddings to news db...
    from concurrent.futures import ThreadPoolExecutor

    num_process = 16
    # Get all product links
    news_contents = check_empty_embeddings_in_news_db()
    # Get the middle index to split the links array in half
    middle_index = len(news_contents) // num_process
    # List of jobs to get executed
    executors_list = []
    # An empty array to save the data
    data = []
    # Create a ThreadPoolExecutor with a maximum of 8 worker threads
    with ThreadPoolExecutor(max_workers=num_process) as executor:
        # Add the two concurrent tasks to scrape product data from different parts of the 'links' list
        for idx in range(num_process):
            executors_list.append(
                executor.submit(
                    insert_embeddings_into_news_db,
                    news_contents[middle_index * idx : middle_index * (idx + 1)],
                )
            )

    # Wait for all tasks to complete
    for x in executors_list:
        pass
