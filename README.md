# Building Vector Search for Financial News with SQLAlchemy and PostgreSQL

Coding environment: Linux in Github Codespaces (Note: Please read the setup guide at https://www.tanyongsheng.com/note/building-vector-search-for-financial-news-with-sqlalchemy-and-postgresql/ for more details)

1. rename `.env.sample` file to `.env`

1. Setting up virtual environment

```
python -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Creating PostgreSQL instances via docker `docker compose up -d`

3. Setting up database: `python -m project.db_models`

4. Scrape stock tickers: `python -m project.tasks.scrape_tickers`

5. Insert stock tickers into database `python -m project.tasks.insert_tickers_db`

6. Scrape news: `python -m project.tasks.scrape_news`

7. Insert news into database: `python -m project.tasks.insert_news_db`

8. Train a spacy model to recognize stock codes, stock symbols, and company name from news text: `python -m project.ml_models.train_extract_tickers`

9. Recognize stock codes, stock symbols, and company name from news text using trained spacy model, and then insert those records into the database table: `python -m project.tasks.insert_news_to_tickers_db`

10. Insert embeddings into database: `python -m project.tasks.insert_news_embedding_db`

11. Perform search for relevant news:
- Full text search: `python -m project.tasks.full_text_search_news`
- Vector search: `python -m project.tasks.vector_search_news`
- Hybrid search: `python -m project.tasks.hybrid_search_news`

## Additional note:

For `project/tasks/scrape_tickers.py` and `project/tasks/insert_news_db.py`, by default, it scrape and inserts news into database table starting from 1 Jan 2024 to 14 Oct 2024, but feel free to change these parameters according to your preference.

Btw, this is just a simple prototype project. Thanks for reading, and hope for more suggestions. And please let me know if you spot any errors.

## Tips
Besides Github Codespaces, you could also try to use GitPod so you could start your coding environment very quickly: https://www.tanyongsheng.com/note/building-vector-search-for-financial-news-with-sqlalchemy-and-postgresql/ (Note: I'm not affiliate with GitPod, and the free plan gives you 50 hours per month at no cost as of 30 Sep 2024.)

This blog has two companion blogs which are Use Cases of (1) [Building Trigram Search for Stock Tickers with Python SQLAlchemy and PostgreSQL](https://www.tanyongsheng.com/note/building-trigram-search-for-stock-tickers-with-python-sqlalchemy-and-postgresql/) and (2) [Name Entity Recognition (NER) with Spacy](https://www.tanyongsheng.com/note/use-cases-of-name-entity-recognition-ner-with-spacy/).
